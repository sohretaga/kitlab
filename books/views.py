from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView, CreateView, ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
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
    success_url = reverse_lazy('index')

    def form_valid(self, form) -> HttpResponse:
        print(form.errors)
        book = form.save(commit=False)
        book.seller = self.request.user
        book.save()
        images = self.request.FILES.getlist('images')

        for image in images:
            Image.objects.create(book=book,image=image)

        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # The parent categories are derived from context_processors.py
        context['publishings'] = Publishing.objects.values('id', 'name')
        context['languages'] = Language.objects.values('id', 'name')
        context['cities'] = City.objects.values('id', 'name')

        return context
    
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
        return get_object_or_404(Book, slug=self.kwargs.get('slug'), is_approved=True)

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