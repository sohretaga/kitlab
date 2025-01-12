from django.urls import path
from .views import (
    IndexView,
    SaleBookView,
    SubCategoriesView,
    BookDetailView,
    CategoryFilterView,
    SuccessSaleView,
    SecondhandBooksView,
    NewBooksView,
    SubCategoryFilterView,
    LoadMoreView
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('secondhand-books', SecondhandBooksView.as_view(), name='secondhand-books'),
    path('new-books', NewBooksView.as_view(), name='new-books'),
    path('sale', SaleBookView.as_view(), name='sale'),
    path('book/<slug:slug>', BookDetailView.as_view(), name='book-detail'),
    path('books/<slug:slug>', CategoryFilterView.as_view(), name='category-filter'),
    path('books/<slug:category_slug>/<slug:subcategory_slug>', SubCategoryFilterView.as_view(), name='subcategory-filter'),
    path('sale/success', SuccessSaleView.as_view(), name='success-sale'),

    # API's
    path('get-sub-categories', SubCategoriesView.as_view()),
    path('load-more-book', LoadMoreView.as_view())
]