from django.urls import path

from .views import PriceListAPIView

app_name = 'prices'

urlpatterns = [
    path('', PriceListAPIView.as_view(), name='price-list'),
]
