from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from typing import Any

from .models import Book, Category, Publishing, Language, City, Condition
from .forms import SaleBookForm

import json

class IndexView(TemplateView):
    template_name = 'index.html'

class SaleBookView(CreateView):
    model = Book
    form_class = SaleBookForm
    template_name = 'sale.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form) -> HttpResponse:
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # The parent categories are derived from context_processors.py
        context['publishings'] = Publishing.objects.values('id', 'name')
        context['languages'] = Language.objects.values('id', 'name')
        context['cities'] = City.objects.values('id', 'name')
        context['conditions'] = Condition.objects.values('id', 'name')

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