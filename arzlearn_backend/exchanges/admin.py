from django.contrib import admin

from .models import Exchange


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'maker_fee', 'taker_fee', 'rating', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
