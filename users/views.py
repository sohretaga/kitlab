from typing import Any
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.forms import BaseModelForm
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .mixins import LogoutRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile

# Create your views here.

class AuthView(LogoutRequiredMixin, TemplateView):
    template_name = 'authenticate.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['login_username'] = self.request.session.pop('login_username', None)
        context['first_name'] = self.request.session.pop('first_name', None)
        context['register_username'] = self.request.session.pop('register_username', None)
        context['email'] = self.request.session.pop('email', None)
        context['mode'] = self.request.session.pop('mode', None)
        context['error'] = self.request.session.pop('error', None)
        return context

class CustomLoginView(LoginView):
    def get_redirect_url(self) -> str:
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_redirect_url()

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        username = form.cleaned_data.get('username')
        self.request.session['login_username'] = username
        return HttpResponseRedirect(reverse_lazy('auth'))

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form: BaseModelForm) -> HttpResponseRedirect:
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        first_name = form.cleaned_data.get('first_name')
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        mode = self.request.POST.get('mode')

        self.request.session['first_name'] = first_name
        self.request.session['register_username'] = username
        self.request.session['email'] = email
        self.request.session['mode'] = mode

        for filed, _ in form.errors.items():
            self.request.session['error'] = filed
            break

        return HttpResponseRedirect(reverse_lazy('auth'))
    
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        user_books = self.request.user.books.all()
        user_favorites = self.request.user.favorites.all()

        context = super().get_context_data(**kwargs)
        context['books_count'] = user_books.count()
        context['books'] = user_books
        context['favorites_count'] = user_favorites.count()
        context['favorites'] = user_favorites

        return context
    
class UpdateProfileView(LoginRequiredMixin, FormView):
    model = Profile
    user_form_class = UserUpdateForm
    profile_form_class = ProfileUpdateForm

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class(request.POST, instance=request.user)
        profile_form = self.profile_form_class(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(reverse_lazy('profile'))