from django.contrib import admin

from .models import Price


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'symbol', 'price_value', 'currency', 'change_percent', 'updated_at')
    list_filter = ('currency',)
    readonly_fields = ('updated_at',)
