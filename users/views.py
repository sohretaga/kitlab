from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
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

    def form_invalid(self, form) -> HttpResponse:
        return HttpResponseRedirect(reverse_lazy('auth'))