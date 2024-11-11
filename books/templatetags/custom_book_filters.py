from django import template

register = template.Library()

@register.filter
def approved_books_count(category):
    return category.books.filter(is_approved=True).count()

@register.filter
def approved_sub_books_count(sub_category):
    return sub_category.sub_books.filter(is_approved=True).count()