import jdatetime
from rest_framework import serializers

from .models import EconomicEvent

PERSIAN_WEEKDAYS = {
    'Saturday': 'شنبه',
    'Sunday': 'یکشنبه',
    'Monday': 'دوشنبه',
    'Tuesday': 'سه‌شنبه',
    'Wednesday': 'چهارشنبه',
    'Thursday': 'پنجشنبه',
    'Friday': 'جمعه',
}


class EconomicEventSerializer(serializers.ModelSerializer):
    day_name_fa = serializers.SerializerMethodField()
    shamsi_date = serializers.SerializerMethodField()

    class Meta:
        model = EconomicEvent
        fields = (
            'id', 'title', 'country', 'importance', 'event_date', 'event_time',
            'shamsi_date', 'day_name_fa', 'actual', 'forecast', 'previous',
        )

    def get_day_name_fa(self, obj):
        return PERSIAN_WEEKDAYS.get(obj.event_date.strftime('%A'), '')

    def get_shamsi_date(self, obj):
        jalali_date = jdatetime.date.fromgregorian(date=obj.event_date)
        return jalali_date.strftime('%Y/%m/%d')
