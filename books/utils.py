from .models import Book
from users.models import Favorite

from django.db.models import OuterRef, Exists

def get_book_objects(request, *args, **kwargs):

    user = request.user
    if user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=user,
            book=OuterRef('pk')
        )
    else:
        is_favorite = Favorite.objects.none()

    return Book.objects.filter(is_approved=True, **kwargs).annotate(
        is_favorite=Exists(is_favorite)
    )