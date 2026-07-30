from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 'display_name', 'email', 'is_email_verified', 'is_staff', 'is_active', 'date_joined',
    )
    list_filter = ('is_staff', 'is_active', 'is_email_verified')
    search_fields = ('username', 'display_name', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تکمیلی', {'fields': ('display_name', 'avatar', 'is_email_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات تکمیلی', {'fields': ('email', 'display_name', 'avatar')}),
    )
