from django.contrib import admin
from .models import Contact, Favorite
# Register your models here.

admin.site.register(Favorite)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'reason', 'short_message', 'created_at')

    def short_message(self, obj):
        return f'{obj.message[:50]}...' if len(obj.message) > 50 else obj.message
    
    short_message.short_description = 'MESAJ'