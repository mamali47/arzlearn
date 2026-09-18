"""
توکن‌های امضاشده و بدون نیاز به دیتابیس.

- ثبت‌نام معلق (Pending Registration): اطلاعات ثبت‌نام کاربر تا وقتی ایمیلش
  را تایید نکرده، هیچ‌جا (نه در دیتابیس) ذخیره نمی‌شود؛ فقط داخل همین توکن
  امضاشده که برایش ایمیل می‌شود نگه‌داری می‌شود. با این روش، تا وقتی کاربر
  روی لینک ایمیلش کلیک نکند، هیچ ردیف CustomUser ای برایش ساخته نمی‌شود.

برای فراموشی رمز عبور از django.contrib.auth.tokens.default_token_generator
استفاده می‌شود (چون آنجا کاربر از قبل در دیتابیس وجود دارد).
"""

from django.core import signing
from django.core.signing import BadSignature, SignatureExpired

PENDING_REGISTRATION_SALT = 'accounts.pending-registration'
PENDING_REGISTRATION_MAX_AGE = 60 * 60 * 24  # ۲۴ ساعت


def make_pending_registration_token(payload: dict) -> str:
    """
    اطلاعات ثبت‌نام (شامل هش رمز عبور، هرگز خود رمز) را امضا و به توکن
    قابل‌ارسال در لینک ایمیل تبدیل می‌کند.
    """
    return signing.dumps(payload, salt=PENDING_REGISTRATION_SALT)


def read_pending_registration_token(token: str):
    """
    توکن را می‌خواند و در صورت معتبر و منقضی‌نشده بودن، دیکشنری اطلاعات
    ثبت‌نام (username, display_name, email, password_hash) را برمی‌گرداند.
    در غیر این صورت None برمی‌گرداند.
    """
    try:
        return signing.loads(
            token, salt=PENDING_REGISTRATION_SALT, max_age=PENDING_REGISTRATION_MAX_AGE
        )
    except (BadSignature, SignatureExpired):
        return None
