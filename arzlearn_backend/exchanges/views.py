from rest_framework import generics, permissions

from .models import Exchange
from .serializers import ExchangeSerializer


class ExchangeListAPIView(generics.ListAPIView):
    """
    GET /api/exchanges/
    لیست صرافی‌های معتبر برای سکشن «بهترین صرافی‌ها» در صفحه اصلی.
    """

    queryset = Exchange.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = ExchangeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
