from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import View, TemplateView, CreateView, ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
from PIL import Image as PilImage
from io import BytesIO
from typing import Any

from .models import Book, Image, Category, Publishing, Language, City, Quote
from .forms import SaleBookForm

import json

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(is_approved=True)
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
        book = get_object_or_404(Book, slug=self.kwargs.get('slug'), is_approved=True)

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
    paginate_by = 16

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)
        return Book.objects.filter(category=category, is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)

        context['category'] = category
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
