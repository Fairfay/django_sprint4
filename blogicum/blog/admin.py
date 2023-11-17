from django.contrib import admin

from .models import Category, Comment, Location, Post


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'post', 'created_at', 'author']
    list_filter = ['created_at', 'author']
    search_fields = ['text', 'author__username', 'post__title']
