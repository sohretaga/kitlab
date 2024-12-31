from django.urls import path
from .views import IndexView, SaleBookView, SubCategoriesView, BookDetailView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('sale', SaleBookView.as_view(), name='sale'),
    path('book/<slug:slug>', BookDetailView.as_view(), name='book-detail'),

    # API's
    path('get-sub-categories', SubCategoriesView.as_view())
]