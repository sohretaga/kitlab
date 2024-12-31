from .models import Category, Book

def categories(request):
    categories = Category.objects.filter(parent__isnull=True)

    return {
        'categories': categories
    }

def suggested_books(request):
    suggestions = Book.objects.filter(is_approved=True).order_by('?')[:4]

    return {
        'suggestions':  suggestions
    }