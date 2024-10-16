from django.urls import path
from .views import IndexView, SaleView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('sale', SaleView.as_view(), name='sale')
]