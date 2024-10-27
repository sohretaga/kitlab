from django import forms
from .models import Book

class SaleBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = (
            "name",
            "category",
            "sub_category",
            "author",
            "publishing",
            "language",
            "city",
            "condition",
            "price",
            "description",
            "cover_photo"
        )