# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('auth/', views.AuthView.as_view(), name='auth'),
    path('auth/login', views.CustomLoginView.as_view(), name='login'),
    path('auth/logout', LogoutView.as_view(next_page='/'), name='logout'),
    path('auth/register', views.RegisterView.as_view(), name='register'),

    path('profile', views.ProfileView.as_view(), name='profile'),
    path('profile/update', views.UpdateProfileView.as_view(), name='update-profile'),
]