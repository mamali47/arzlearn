from django.contrib import admin
from django.utils.html import format_html

from .models import TopBanner


@admin.register(TopBanner)
class TopBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'preview', 'link_url', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    readonly_fields = ('generated_preview', 'created_at')

    fieldsets = (
        ('محتوای بنر', {
            'fields': ('image', 'image_mobile', 'alt_text', 'link_url', 'is_active'),
        }),
        ('اندازه و برش (اختیاری — مقادیر پیش‌فرض برای اکثر بنرها مناسب است)', {
            'fields': (
                'display_height_desktop', 'display_height_mobile', 'fit_mode', 'focus',
            ),
            'description': (
                'ارتفاع نوار بنر ثابت است و با تغییر اندازه‌ی پنجره کوچک و بزرگ '
                'نمی‌شود. تصویر آپلودشده خودکار برای همین ابعاد بهینه می‌شود؛ '
                'نسخه‌ی موبایل جداگانه و بلندتر ساخته می‌شود تا متن بنر روی '
                'گوشی خوانا بماند.'
            ),
        }),
        ('پیش‌نمایش نسخه‌های ساخته‌شده', {
            'fields': ('generated_preview', 'created_at'),
        }),
    )

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.desktop_jpeg:
            return format_html('<img src="{}" style="height:34px;border-radius:4px" />',
                               obj.desktop_jpeg.url)
        return '—'

    @admin.display(description='نسخه‌های خودکار')
    def generated_preview(self, obj):
        if not obj.pk or not obj.desktop_jpeg:
            return 'بعد از ذخیره ساخته می‌شود.'
        return format_html(
            '<div style="display:flex;gap:24px;flex-wrap:wrap">'
            '<div><b>دسکتاپ ({}×{})</b><br><img src="{}" style="max-width:520px;border-radius:6px" /></div>'
            '<div><b>موبایل ({}×{})</b><br><img src="{}" style="max-width:260px;border-radius:6px" /></div>'
            '</div>',
            obj.desktop_width, obj.desktop_height, obj.desktop_jpeg.url,
            obj.mobile_width, obj.mobile_height, obj.mobile_jpeg.url,
        )
