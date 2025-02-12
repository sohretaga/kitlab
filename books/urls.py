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
    LoadMoreView,
    SearchBookNameView,
    SearchBookView
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
    path('search', SearchBookView.as_view(), name='search'),

    # API's
    path('api/get-sub-categories', SubCategoriesView.as_view()),
    path('api/load-more-book', LoadMoreView.as_view()),
    path('api/search-book-name', SearchBookNameView.as_view()),
]