from django.contrib import admin

from .models import TopBanner


@admin.register(TopBanner)
class TopBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'link_url', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
