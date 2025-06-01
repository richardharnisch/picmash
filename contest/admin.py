from django.contrib import admin
from .models import ImageEntry

@admin.register(ImageEntry)
class ImageEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating')
    readonly_fields = ('score',)
