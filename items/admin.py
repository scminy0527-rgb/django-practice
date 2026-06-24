from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'thumbnail_url']
    fields = ['name', 'detail', 'stock', 'price', 'thumbnail_url']
