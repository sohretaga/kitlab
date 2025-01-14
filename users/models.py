from django.db import models
from django.contrib.auth.models import User
from books.models import Book, City

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    telegram = models.CharField(max_length=32, blank=True, null=True)
    instagram = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

class Contact(models.Model):
    REASON_CHOICES = [
        ('offer', 'Təklif'),
        ('remark', 'İrad'),
        ('error', 'Xəta'),
        ('collaboration', 'Əməkdaşlıq'),
        ('other', 'Digər')
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.IntegerField(blank=True, null=True)
    reason = models.CharField(max_length=13, choices=REASON_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Əlaqə'
        verbose_name_plural = 'Əlaqələr'

    def __str__(self):
        return self.full_name