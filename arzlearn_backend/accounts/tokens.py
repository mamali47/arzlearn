"""
توکن‌های یک‌بارمصرف/موقت برای تایید ایمیل.

برای فراموشی رمز عبور از django.contrib.auth.tokens.default_token_generator
استفاده می‌کنیم (توکن استاندارد خود جنگو) که نیازی به ذخیره‌سازی در دیتابیس
ندارد و به‌محض تغییر رمز عبور کاربر، خودکار باطل می‌شود. برای همین نیازی به
فایل جداگانه برایش نیست.
"""

from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

EMAIL_VERIFICATION_SALT = 'accounts.email-verification'
EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 24  # 24 ساعت


def make_email_verification_token(user) -> str:
    """یک توکن امضاشده و دارای مهر زمانی برای تایید ایمیل کاربر می‌سازد."""
    signer = TimestampSigner(salt=EMAIL_VERIFICATION_SALT)
    return signer.sign(str(user.pk))


def read_email_verification_token(token: str):
    """
    توکن را می‌خواند و در صورت معتبر و منقضی‌نشده بودن، شناسه‌ی کاربر (pk)
    را به‌صورت int برمی‌گرداند. در غیر این صورت None برمی‌گرداند.
    """
    signer = TimestampSigner(salt=EMAIL_VERIFICATION_SALT)
    try:
        value = signer.unsign(token, max_age=EMAIL_VERIFICATION_MAX_AGE)
        return int(value)
    except (BadSignature, SignatureExpired, ValueError):
        return None
