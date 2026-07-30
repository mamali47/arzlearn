from django.contrib import admin
from django.utils.html import format_html

from .models import EconomicEvent

IMPORTANCE_COLORS = {
    'high': '#dc2626',
    'medium': '#f59e0b',
    'low': '#eab308',
}


@admin.register(EconomicEvent)
class EconomicEventAdmin(admin.ModelAdmin):
    """
    مدیریت دستی رویدادهای تقویم اقتصادی. چون فعلاً منبع خودکار (API) در
    دسترس نیست، این ادمین طوری تنظیم شده که وارد کردن هفتگی رویدادها
    سریع و راحت باشد:
      - می‌توانید مستقیماً از داخل لیست (بدون باز کردن هر رویداد) اهمیت،
        ساعت، و مقادیر واقعی/پیش‌بینی/قبلی را ویرایش و همه را یک‌جا Save کنید.
      - فیلتر بر اساس تاریخ و اهمیت برای پیدا کردن سریع رویدادهای هفته.
    """

    list_display = (
        'title', 'country', 'importance_badge', 'event_date', 'event_time',
        'actual', 'forecast', 'previous',
    )
    list_editable = ('event_time', 'actual', 'forecast', 'previous')
    list_filter = ('importance', 'country', 'event_date')
    search_fields = ('title', 'country')
    date_hierarchy = 'event_date'
    ordering = ('event_date', 'event_time')
    list_per_page = 50

    fieldsets = (
        (None, {
            'fields': ('title', 'country', 'importance', 'event_date', 'event_time')
        }),
        ('مقادیر', {
            'fields': ('actual', 'forecast', 'previous'),
            'description': 'می‌توانید این مقادیر را بعداً (نزدیک زمان رویداد یا بعد از انتشار) تکمیل/ویرایش کنید.',
        }),
    )

    def importance_badge(self, obj):
        color = IMPORTANCE_COLORS.get(obj.importance, '#999')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 10px; border-radius:999px; font-size:12px;">{}</span>',
            color, obj.get_importance_display(),
        )

    importance_badge.short_description = 'اهمیت'
