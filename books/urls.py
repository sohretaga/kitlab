from django.urls import path
from .views import IndexView, SaleBookView, SubCategoriesView, BookDetailView, CategoryFilterView, SuccessSaleView, SecondhandBooksView, NewBooksView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('secondhand-books', SecondhandBooksView.as_view(), name='secondhand-books'),
    path('new-books', NewBooksView.as_view(), name='new-books'),
    path('sale', SaleBookView.as_view(), name='sale'),
    path('book/<slug:slug>', BookDetailView.as_view(), name='book-detail'),
    path('category/<slug:slug>', CategoryFilterView.as_view(), name='category-filter'),
    path('sale/success', SuccessSaleView.as_view(), name='success-sale'),

    # API's
    path('get-sub-categories', SubCategoriesView.as_view())
]