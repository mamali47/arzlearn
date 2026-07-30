import re

from rest_framework import serializers

# الگوی تشخیص لینک: آدرس‌های http(s)، www.، یا دامنه‌های رایج
LINK_PATTERN = re.compile(
    r'(https?://|www\.|\b[a-zA-Z0-9-]+\.(com|ir|net|org|io|co|info|biz|me|tv|xyz|app)\b)',
    re.IGNORECASE,
)


def validate_no_links(body):
    """جلوگیری از ثبت لینک در دیدگاه‌ها (برای جلوگیری از اسپم/تبلیغات/فیشینگ)."""
    if LINK_PATTERN.search(body):
        raise serializers.ValidationError('ثبت لینک در دیدگاه‌ها مجاز نیست.')
    return body
