"""
توابع کمکی برای ارسال ایمیل‌های تایید ایمیل (ثبت‌نام) و بازیابی رمز عبور.
از تنظیمات SMTP که در settings.py (متغیرهای محیطی EMAIL_*) مشخص شده استفاده می‌کند.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verification_email(email: str, display_name: str, token: str) -> None:
    """
    توجه: چون در این مرحله هنوز کاربری در دیتابیس ساخته نشده (ثبت‌نام معلق
    است)، به‌جای یک آبجکت User، مستقیماً ایمیل و نام نمایشی را می‌گیریم.
    """
    verify_url = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"
    html_message = render_to_string(
        'emails/verify_email.html',
        {'display_name': display_name, 'verify_url': verify_url},
    )
    send_mail(
        subject='تایید ایمیل - ارزلرن',
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user, uid: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?uid={uid}&token={token}"
    html_message = render_to_string(
        'emails/reset_password.html',
        {'user': user, 'reset_url': reset_url},
    )
    send_mail(
        subject='بازیابی رمز عبور - ارزلرن',
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
