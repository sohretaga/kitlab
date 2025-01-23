from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import View, TemplateView, CreateView, ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Exists, Subquery, OuterRef, F, Q
from django.conf import settings
from PIL import Image as PilImage
from io import BytesIO
from typing import Any

from .models import Book, Image, Category, Publishing, Language, City, Quote
from .forms import SaleBookForm
from .utils import get_book_objects
from users.models import Favorite

import json

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        books = get_book_objects(self.request)
        paginator = Paginator(books, 16)
        # reset book filter for LoadMoreView
        self.request.session['book_filter'] = {}
        try:
            books_page = paginator.page(page)
        except EmptyPage:
            books_page = paginator.page(paginator.num_pages)

        context['books'] = books_page.object_list
        context['quote'] = Quote.get_random_quote()

        return context

class SaleBookView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = SaleBookForm
    template_name = 'sale.html'
    success_url = reverse_lazy('success-sale')

    def form_valid(self, form) -> HttpResponse:
        book = form.save(commit=False)
        book.seller = self.request.user
        book.cover_photo = self.optimize_image(form.cleaned_data.get('cover_photo'))

        # Saves the selected city to the profile for auto-selection in future listings, speeding up the process.
        city = form.cleaned_data.get('city')
        if book.seller.profile.city != city:
            book.seller.profile.city = city
            book.seller.profile.save()

        book.save()
        self.request.session['success_sale'] = book.slug
        images = self.request.FILES.getlist('images')

        for image in images:
            optimized_image = self.optimize_image(image)
            Image.objects.create(book=book, image=optimized_image)

        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # The parent categories are derived from context_processors.py
        context['publishings'] = Publishing.objects.values('id', 'name')
        context['languages'] = Language.objects.values('id', 'name')
        context['cities'] = City.objects.values('id', 'name')

        return context

    def optimize_image(self, uploaded_image):
        """
        Optimize the uploaded image and convert it to WebP format.
        """
        with PilImage.open(uploaded_image) as img:
            # Fix orientation if EXIF data is available
            exif = img._getexif()
            orientation = exif.get(274) if exif else None  # 274 is the Orientation tag
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

            # Convert image to RGB if not already in RGB mode
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize image to reduce dimensions (optional, set max size)
            max_size = (800, 800)  # Change this size as needed
            img.thumbnail(max_size, PilImage.Resampling.LANCZOS)

            # Save the image to a BytesIO object in WebP format
            buffer = BytesIO()
            img.save(buffer, format="WEBP", quality=80)  # Adjust quality as needed
            buffer.seek(0)

            # Create a new ContentFile for saving to the database
            optimized_image = ContentFile(buffer.read(), name=f"{uploaded_image.name.split('.')[0]}.webp")
            return optimized_image

class SubCategoriesView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category_id = data.get('id')

        if not category_id:
            return JsonResponse({'error': 'No category ID provided'}, status=400)

        category = get_object_or_404(Category, id=category_id)
        sub_categories = category.childrens.all()
        sub_categories_list = list(sub_categories.values('id', 'name'))

        return JsonResponse(sub_categories_list, safe=False)

class BookDetailView(DetailView):
    model = Book
    template_name = 'detail.html'
    context_object_name = 'book'

    def get_object(self, queryset = ...):

        if self.request.user.is_authenticated:
            is_favorite = Favorite.objects.filter(
                user=self.request.user,
                book=OuterRef('pk')
            )
        else:
            is_favorite = Favorite.objects.none()

        book_queryset = Book.objects.filter(
            slug=self.kwargs.get('slug'),
            is_approved=True
        ).annotate(
            is_favorite=Exists(is_favorite)
        )

        book = book_queryset.first()
        if not book:
            raise Http404("Book not found")

        if book:
            viewed_books = self.request.session.get('viewed_books', [])
            if book.id not in viewed_books:
                book.view_count += 1
                book.save()
                viewed_books.append(book.id)
                self.request.session['viewed_books'] = viewed_books

        return book

class CategoryFilterView(ListView):
    model = Book
    template_name = 'book-filter.html'
    context_object_name = 'books'
    paginate_by = settings.DEFAULT_PAGINATE_BY

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)
        book_filter = {'category__slug': category.slug}
        # store filtering criteria in session for LoadMoreView
        self.request.session['book_filter'] = book_filter
        return Book.objects.filter(**book_filter, is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)
        context['page_title'] = category.name
        return context
    
class SubCategoryFilterView(ListView):
    model = Book
    template_name = 'book-filter.html'
    context_object_name = 'books'
    paginate_by = settings.DEFAULT_PAGINATE_BY

    def get_category_and_subcategory(self):
        """Helper method to fetch category and subcategory."""
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        category = get_object_or_404(Category, slug=category_slug)
        sub_category = get_object_or_404(Category, slug=subcategory_slug)
        return category, sub_category

    def get_queryset(self):
        category, sub_category = self.get_category_and_subcategory()
        book_filter = {
            'category__slug': category.slug,
            'sub_category__slug': sub_category.slug,
        }
        # store filtering criteria in session for LoadMoreView
        self.request.session['book_filter'] = book_filter
        return Book.objects.filter(**book_filter, is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category, sub_category = self.get_category_and_subcategory()
        context['page_title'] = f'{category.name} > {sub_category.name}'
        return context
    
class SuccessSaleView(LoginRequiredMixin, TemplateView):
    template_name = 'success-sale.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        success_sale = self.request.session.pop('success_sale', None)
        if success_sale:
            context['success_sale'] = success_sale
            return context
        
        raise Http404('Success sale not found.')

class SecondhandBooksView(ListView):
    model = Book
    template_name = 'book-filter.html'
    context_object_name = 'books'
    paginate_by = settings.DEFAULT_PAGINATE_BY

    def get_queryset(self):
        book_filter = {'new': False}
        # store filtering criteria in session for LoadMoreView
        self.request.session['book_filter'] = book_filter
        return  get_book_objects(self.request, **book_filter)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'İkinci Əl Kitablar'
        return context
    
class NewBooksView(ListView):
    model = Book
    template_name = 'book-filter.html'
    context_object_name = 'books'
    paginate_by = settings.DEFAULT_PAGINATE_BY

    def get_queryset(self):
        book_filter = {'new': True}
        # store filtering criteria in session for LoadMoreView
        self.request.session['book_filter'] = book_filter
        return get_book_objects(self.request, **book_filter)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Yeni Kitablar'
        return context
    
class LoadMoreView(ListView):
    model = Book
    paginate_by = settings.DEFAULT_PAGINATE_BY

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        book_filter:dict = self.request.session.get('book_filter', {})

        # If the query comes from the search page, this part works.
        query = book_filter.get('q')
        if query:
            books = Book.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(author__icontains=query),
                is_approved=True)
        else:
            books = Book.objects.filter(**book_filter, is_approved=True)

        paginator = Paginator(books, self.paginate_by)

        try:
            hover_image = Image.objects.filter(
                book=OuterRef('pk')
            ).values('image')

            if request.user.is_authenticated:
                is_favorite = Favorite.objects.filter(
                    user=request.user,
                    book=OuterRef('pk')
                )
            else:
                is_favorite = Favorite.objects.none()

            books_page = paginator.page(page)
            loaded_books = books_page.object_list.annotate(
                hover_image=Subquery(hover_image[:1]),
                category_name=F('category__name'),
                is_favorite=Exists(is_favorite)
            )

            books_data = list(loaded_books.values(
                'id', 'name', 'slug', 'cover_photo', 'hover_image', 'category_name', 'is_approved', 'new', 'price', 'is_favorite'
            ))

            return JsonResponse({
                'books': books_data,
                'has_next': books_page.has_next()
            })

        except EmptyPage:
            return JsonResponse({
                'books': [],
                'has_next': False
            })
        
class SearchBookNameView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if query:
            books = Book.objects.filter(name__icontains=query, is_approved=True)[:10].values('name', 'slug', 'author')
            
            return JsonResponse({
                'books': list(books)
            }, safe=False)

        return JsonResponse({
            'books': []
        }, safe=False)
    
class SearchBookView(ListView):
    model = Book
    template_name = 'book-filter.html'
    context_object_name = 'books'
    paginate_by = settings.DEFAULT_PAGINATE_BY

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            book_filter = {'q': query}
            
            # store filtering criteria in session for LoadMoreView
            self.request.session['book_filter'] = book_filter
            return get_book_objects(
                self.request,
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(author__icontains=query)
            )

        return Book.objects.none()
    
    def get_context_data(self, **kwargs):
        query = self.request.GET.get('q', '')
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Axtarış: {query}'
        return context