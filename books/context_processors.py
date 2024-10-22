from .models import Category

def categories(request):
    categories = Category.objects.filter(parent__isnull=True)

    return {
        'categories': categories
    }