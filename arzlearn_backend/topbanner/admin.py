from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    fields = (
        "title",
        "url",
        "image_desktop",
        "image_mobile",
        "alt_text",
        "is_active",
    )
