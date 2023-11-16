from django.contrib import admin

from .models import Category, Location, Post


class PublishedModelAdmin(admin.ModelAdmin):
    list_display = ['is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['created_at']


@admin.register(Category)
class CategoryAdmin(PublishedModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(PublishedModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(PublishedModelAdmin):
    list_filter = ['is_published', 'created_at', 'author',
                   'category', 'location']
    date_hierarchy = 'created_at'
