"""
سرویس دریافت رویدادهای تقویم اقتصادی از یک API خارجی.

⚠️ نکته‌ی مهم برای توسعه‌دهنده:
این کد بر پایه‌ی مستندات عمومی چند سرویس تقویم اقتصادی (مثل forex-calendar.pro)
نوشته شده که سطح اهمیت رویدادها را HIGH/MEDIUM/LOW برمی‌گردانند (دقیقاً معادل
قرمز/نارنجی/زرد که خواسته شده بود). چون این محیط توسعه به اینترنت دسترسی
نداشت، امکان تست زنده‌ی این API وجود نداشت. شما باید:
  1. در یکی از این سرویس‌ها ثبت‌نام کرده و یک API Key رایگان بگیرید
     (مثلاً forex-calendar.pro یا مشابه آن).
  2. مقدار ECONOMIC_CALENDAR_API_KEY و در صورت نیاز ECONOMIC_CALENDAR_API_BASE_URL
     را در فایل .env تنظیم کنید.
  3. بعد از اولین اجرای دستور `update_economic_calendar`، خروجی واقعی API را با
     پاسخ لاگ‌شده مقایسه کنید؛ در صورت متفاوت بودن نام فیلدها (مثلاً "name" به‌جای
     "title")، تابع `_parse_event` در همین فایل را با نام فیلدهای واقعی هماهنگ کنید.
این تابع طوری نوشته شده که چند نام رایج فیلد را همزمان امتحان می‌کند تا با
بیشتر سرویس‌های مشابه سازگار باشد، اما تضمین ۱۰۰ درصدی برای هر API ای وجود ندارد.
"""

import logging
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# نگاشت سطح اهمیت از مقادیر رایج APIها به مقادیر مدل ما
IMPORTANCE_MAP = {
    'HIGH': 'high', 'MEDIUM': 'medium', 'LOW': 'low',
    'high': 'high', 'medium': 'medium', 'low': 'low',
    '3': 'high', '2': 'medium', '1': 'low',
    3: 'high', 2: 'medium', 1: 'low',
}


def _get_first(data, *keys, default=None):
    """اولین مقدار غیرخالی را از بین چند نام احتمالی فیلد برمی‌گرداند."""
    for key in keys:
        if key in data and data[key] not in (None, ''):
            return data[key]
    return default


def _parse_event(raw_event):
    """
    یک رویداد خام از پاسخ API را به یک دیکشنری استاندارد (متناسب با مدل
    EconomicEvent) تبدیل می‌کند. چند نام رایج فیلد را امتحان می‌کند تا با
    ساختارهای مختلف APIها سازگار باشد.
    """
    title = _get_first(raw_event, 'title', 'name', 'event')
    country = _get_first(raw_event, 'country', 'currency', default='')
    raw_importance = _get_first(raw_event, 'importance', 'impact', default='low')
    importance = IMPORTANCE_MAP.get(raw_importance, 'low')

    raw_datetime = _get_first(raw_event, 'datetime', 'date', 'event_date')
    event_date = None
    event_time = None
    if raw_datetime:
        try:
            parsed = datetime.fromisoformat(str(raw_datetime).replace('Z', '+00:00'))
            event_date = parsed.date()
            event_time = parsed.time()
        except ValueError:
            try:
                event_date = datetime.strptime(str(raw_datetime)[:10], '%Y-%m-%d').date()
            except ValueError:
                logger.warning('تاریخ رویداد قابل تجزیه نبود: %s', raw_datetime)
                return None

    if not title or not event_date:
        logger.warning('رویداد خام فاقد عنوان یا تاریخ معتبر بود: %s', raw_event)
        return None

    return {
        'title': str(title)[:200],
        'country': str(country)[:10],
        'importance': importance,
        'event_date': event_date,
        'event_time': event_time,
        'actual': str(_get_first(raw_event, 'actual', default='') or '')[:30],
        'forecast': str(_get_first(raw_event, 'forecast', 'consensus', default='') or '')[:30],
        'previous': str(_get_first(raw_event, 'previous', default='') or '')[:30],
    }


def fetch_week_events(week_start, week_end):
    """
    رویدادهای اقتصادی یک بازه‌ی زمانی را از API خارجی می‌گیرد.
    خروجی: لیستی از دیکشنری‌های استاندارد (خروجی _parse_event) یا [] در صورت خطا.
    """
    api_key = settings.ECONOMIC_CALENDAR_API_KEY
    base_url = settings.ECONOMIC_CALENDAR_API_BASE_URL.rstrip('/')

    if not api_key:
        logger.warning(
            'ECONOMIC_CALENDAR_API_KEY تنظیم نشده؛ دریافت تقویم اقتصادی نادیده گرفته شد. '
            'برای فعال‌سازی، یک کلید API از سرویس تقویم اقتصادی دلخواه بگیرید و در .env قرار دهید.'
        )
        return []

    try:
        response = requests.get(
            f'{base_url}/events',
            headers={'X-API-Key': api_key},
            params={
                'date_from': week_start.isoformat(),
                'date_to': week_end.isoformat(),
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        raw_events = _get_first(data, 'events', 'data', 'results', default=[])
        parsed_events = [event for event in (_parse_event(e) for e in raw_events) if event]

        if not parsed_events:
            logger.warning(
                'هیچ رویدادی از API تقویم اقتصادی استخراج نشد. نمونه‌ی خام پاسخ '
                '(برای بررسی ساختار واقعی فیلدها): %s', str(data)[:500],
            )

        return parsed_events

    except (requests.RequestException, ValueError) as exc:
        logger.error('خطا در دریافت تقویم اقتصادی: %s', exc)
        return []


def update_week_economic_events():
    """
    یک چرخه‌ی کامل بروزرسانی: رویدادهای هفته‌ی جاری (شنبه تا جمعه) را می‌گیرد
    و در دیتابیس ذخیره می‌کند (رویدادهای قدیمی همان بازه حذف و جایگزین می‌شوند).
    """
    from .models import EconomicEvent

    today = timezone.localdate()
    days_since_saturday = (today.weekday() - 5) % 7
    week_start = today - timedelta(days=days_since_saturday)
    week_end = week_start + timedelta(days=6)

    events_data = fetch_week_events(week_start, week_end)
    if not events_data:
        return 0

    EconomicEvent.objects.filter(event_date__gte=week_start, event_date__lte=week_end).delete()

    created_events = [EconomicEvent(**event_data) for event_data in events_data]
    EconomicEvent.objects.bulk_create(created_events)

    logger.info('تعداد %d رویداد اقتصادی برای هفته %s تا %s ذخیره شد.', len(created_events), week_start, week_end)
    return len(created_events)
