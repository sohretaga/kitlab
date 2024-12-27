from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Image, Book
import os

@receiver(post_delete, sender=Image)
def delete_book_images(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(post_delete, sender=Book)
def delete_book_cover(sender, instance, **kwargs):
    if instance.cover_photo:
        if os.path.isfile(instance.cover_photo.path):
            os.remove(instance.cover_photo.path)