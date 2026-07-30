from rest_framework import generics, permissions

from .models import Price
from .serializers import PriceSerializer


class PriceListAPIView(generics.ListAPIView):
    """
    GET /api/prices/
    قیمت لحظه‌ای بیت‌کوین، اتریوم، سولانا، تتر و طلای ۱۸ عیار.
    فرانت‌اند برای بروزرسانی هر ثانیه، این endpoint را poll می‌کند
    (یا در فاز ۴ از طریق WebSocket لحظه‌ای دریافت می‌کند).
    """

    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
