from django.urls import path
from .views import IndexView, SaleBookView, SubCategoriesView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('sale', SaleBookView.as_view(), name='sale'),

    # API's
    path('get-sub-categories', SubCategoriesView.as_view())
]