from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('body', 'user__username', 'article__title')
    autocomplete_fields = ('article', 'user', 'parent')
    date_hierarchy = 'created_at'
