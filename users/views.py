from typing import Any
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .mixins import LogoutRequiredMixin

# Create your views here.

class AuthView(LogoutRequiredMixin, TemplateView):
    template_name = 'authenticate.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.session.pop('username', None)
        return context

class CustomLoginView(LoginView):
    def get_redirect_url(self) -> str:
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_redirect_url()

    def form_invalid(self, form) -> HttpResponse:
        username = form.cleaned_data.get('username')
        self.request.session['username'] = username
        return HttpResponseRedirect(reverse_lazy('auth'))