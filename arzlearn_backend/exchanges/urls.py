from django.urls import path

from .views import ExchangeListAPIView

app_name = 'exchanges'

urlpatterns = [
    path('', ExchangeListAPIView.as_view(), name='exchange-list'),
]
