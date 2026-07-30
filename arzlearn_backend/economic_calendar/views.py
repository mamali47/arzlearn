from datetime import timedelta

from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone
from rest_framework import generics, permissions

from .models import EconomicEvent
from .serializers import EconomicEventSerializer

# ترتیب اهمیت برای مرتب‌سازی: بسیار مهم (قرمز) اول، بعد نارنجی، بعد زرد
IMPORTANCE_ORDER = Case(
    When(importance='high', then=Value(0)),
    When(importance='medium', then=Value(1)),
    When(importance='low', then=Value(2)),
    output_field=IntegerField(),
)


def _get_current_week_range():
    """
    بازه‌ی هفته‌ی جاری بر اساس هفته‌ی ایرانی (شنبه تا جمعه) را برمی‌گرداند.
    """
    today = timezone.localdate()
    # Python weekday(): Monday=0 ... Saturday=5, Sunday=6
    days_since_saturday = (today.weekday() - 5) % 7
    week_start = today - timedelta(days=days_since_saturday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


class TodayEconomicEventsAPIView(generics.ListAPIView):
    """
    GET /api/economic-calendar/today/
    مهم‌ترین رویدادهای اقتصادی امروز (برای سکشن صفحه اصلی)، حداکثر ۸ مورد.

    منطق فیلتر بر اساس اهمیت:
    - «زرد» (کم‌اهمیت) هیچ‌وقت در این سکشن نمایش داده نمی‌شود.
    - اگر ۲ رویداد «قرمز» یا بیشتر امروز داشتیم، فقط قرمزها نمایش داده می‌شوند.
    - اگر کمتر از ۲ رویداد قرمز داشتیم (صفر یا یک)، «نارنجی» هم به لیست اضافه می‌شود.
    """

    serializer_class = EconomicEventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        today = timezone.localdate()
        today_events = EconomicEvent.objects.filter(event_date=today)

        red_count = today_events.filter(importance='high').count()

        if red_count >= 2:
            allowed_importances = ['high']
        else:
            allowed_importances = ['high', 'medium']

        return (
            today_events.filter(importance__in=allowed_importances)
            .annotate(importance_rank=IMPORTANCE_ORDER)
            .order_by('importance_rank', 'event_time')[:8]
        )


class WeekEconomicEventsAPIView(generics.ListAPIView):
    """
    GET /api/economic-calendar/week/
    تمام رویدادهای هفته‌ی جاری (شنبه تا جمعه) برای صفحه‌ی اختصاصی تقویم اقتصادی.
    """

    serializer_class = EconomicEventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        week_start, week_end = _get_current_week_range()
        return (
            EconomicEvent.objects.filter(event_date__gte=week_start, event_date__lte=week_end)
            .annotate(importance_rank=IMPORTANCE_ORDER)
            .order_by('event_date', 'event_time', 'importance_rank')
        )
