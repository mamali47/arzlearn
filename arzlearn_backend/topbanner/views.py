from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TopBanner
from .serializers import TopBannerSerializer


class ActiveTopBannerAPIView(APIView):
    """
    GET /api/topbanner/active/
    اگر بنر فعالی وجود داشته باشد، اطلاعاتش را برمی‌گرداند؛ در غیر این
    صورت null (تا فرانت‌اند بفهمد این قسمت را اصلاً نمایش ندهد).
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        banner = TopBanner.objects.filter(is_active=True).first()
        if not banner:
            return Response(None)
        serializer = TopBannerSerializer(banner, context={'request': request})
        return Response(serializer.data)
