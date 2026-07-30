from django.urls import path

from .views import TodayEconomicEventsAPIView, WeekEconomicEventsAPIView

app_name = 'economic_calendar'

urlpatterns = [
    path('today/', TodayEconomicEventsAPIView.as_view(), name='today'),
    path('week/', WeekEconomicEventsAPIView.as_view(), name='week'),
]
