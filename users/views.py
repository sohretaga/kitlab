from typing import Any
from django.shortcuts import redirect, get_object_or_404
from django.forms import BaseModelForm
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Exists, Subquery, F

from .mixins import LogoutRequiredMixin
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, ContactForm
from .models import Profile, Favorite
from books.models import Book, Image

import json

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

class CustomLoginView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', reverse_lazy('index'))
            return HttpResponseRedirect(next_url)
        else:
            request.session['login_username'] = username
            return HttpResponseRedirect(reverse_lazy('auth'))

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('auth'))

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form: BaseModelForm) -> HttpResponseRedirect:
        response = super().form_valid(form)
        user = form.save(commit=False)
        user.username = form.cleaned_data.get('username').lower()
        user.email = form.cleaned_data.get('email').lower()
        user.save()
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

        user = self.request.user
        if user.is_authenticated:
            is_favorite = Favorite.objects.filter(
                user=user,
                book=OuterRef('pk')
            )
        else:
            is_favorite = Favorite.objects.none()

        user_books = self.request.user.books.annotate(
            is_favorite=Exists(is_favorite)
        )

        context = super().get_context_data(**kwargs)
        context['books_count'] = user_books.count()
        context['books'] = user_books

        book_filter = {'seller__username': self.request.user.username}
        # store filtering criteria in session for books.models.LoadMoreView
        self.request.session['book_filter'] = book_filter

        return context
    
class UpdateProfileView(LoginRequiredMixin, FormView):
    model = Profile
    user_form_class = UserUpdateForm
    profile_form_class = ProfileUpdateForm

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class(request.POST, instance=request.user)
        profile_form = self.profile_form_class(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_instance = user_form.save(commit=False)
            user_instance.username = user_form.cleaned_data.get('username').lower()
            user_instance.email = user_form.cleaned_data.get('email').lower()
            user_instance.save()
            profile_form.save()

            return redirect(reverse_lazy('profile'))

class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        form.save()
        return self.render_to_response(
            self.get_context_data(form_success=True)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_success'] = kwargs.get('form_success', '')
        return context

class FavoriteBookView(View):
    def post(self, request, *args, **kwargs):
        """
        Add or remove book from favorites
        """
        user=request.user

        if not user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        body = json.loads(request.body)
        book_id = body.get('book_id')
        book = get_object_or_404(Book, id=book_id)

        # Check favorite
        favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
        if created:
            return JsonResponse({
                    'message': 'Book added to favorites',
                    'created': created
                }, status=201)

        favorite.delete()
        return JsonResponse({
                'message': 'Book removed from favorites',
                'created': created
            }, status=200)

class UserFavoriteBooks(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):

        user = self.request.user
        is_favorite = Favorite.objects.filter(
            user=user,
            book=OuterRef('book_id')
        )

        hover_image = Image.objects.filter(
            book=OuterRef('book_id')
        ).values('image')

        user_fovorites = self.request.user.favorites.annotate(
            name=F('book__name'),
            slug=F('book__slug'),
            cover_photo=F('book__cover_photo'),
            hover_image=Subquery(hover_image[:1]),
            category_name=F('book__category__name'),
            is_approved=F('book__is_approved'),
            new=F('book__new'),
            price=F('book__price'),
            is_favorite=Exists(is_favorite)
        ).values(
            'book_id',
            'name',
            'slug',
            'cover_photo',
            'hover_image',
            'category_name',
            'is_approved',
            'new',
            'price',
            'is_favorite'
        )

        return JsonResponse({
            'books': list(user_fovorites),
        }, status=200)