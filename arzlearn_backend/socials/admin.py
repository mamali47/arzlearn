from django.contrib import admin

from .models import SocialLink


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('platform_name', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('platform_name',)
