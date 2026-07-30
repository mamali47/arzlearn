from rest_framework import generics, permissions

from .models import SocialLink
from .serializers import SocialLinkSerializer


class SocialLinkListAPIView(generics.ListAPIView):
    """
    GET /api/socials/
    آیتم‌های بخش «ارزلرن در شبکه‌های اجتماعی» در فوتر.
    """

    queryset = SocialLink.objects.filter(is_active=True).order_by('order')
    serializer_class = SocialLinkSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
