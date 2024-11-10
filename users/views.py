from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from .mixins import LogoutRequiredMixin

# Create your views here.

class AuthView(LogoutRequiredMixin, TemplateView):
    template_name = 'authenticate.html'

class CustomLoginView(LoginView):
    def get_redirect_url(self) -> str:
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_redirect_url()