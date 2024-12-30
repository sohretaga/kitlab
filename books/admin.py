from django.contrib import admin
from .models import Category, Publishing, Language, City, Book, Quote

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'parent_category')
    prepopulated_fields = {'slug': ('name',)}

    def parent_category(self, obj):
        # Return False if the category has a parent (meaning it's not a main category),
        # otherwise return True, indicating it is a main category.
        return False if obj.parent else True
    
    parent_category.boolean = True
    parent_category.short_description = 'ƏSAS KATEQORİYA'

@admin.register(Publishing)
class PublishingAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_approved',
        'created_at',
        'category_path',
        'publishing',
        'language',
        'city',
        'new',
        'price'
    )

    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('is_approved',)
    list_filter = ('is_approved', 'created_at')

    def category_path(self, obj):
        """
        If the parent field is selected in the Category model, 
        this method returns the full category path based on the hierarchy.
        """
        return obj.sub_category
    
    category_path.short_description = 'KATEQORİYA'

admin.site.register(Quote)