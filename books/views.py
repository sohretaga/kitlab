from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'index.html'

class SaleView(TemplateView):
    template_name = 'sale.html'