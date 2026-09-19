from rest_framework import serializers

from .models import TopBanner


class TopBannerSerializer(serializers.ModelSerializer):
    """
    خروجی این سریالایزر همه‌ی چیزی است که فرانت‌اند برای نمایش بنر بدون
    «پریدن صفحه» (layout shift) لازم دارد: آدرس نسخه‌ی WebP و JPEG برای
    دسکتاپ و موبایل، ابعاد دقیق هر کدام، ارتفاع نمایشی و رنگ پس‌زمینه.
    """

    desktop = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    # برای سازگاری با نسخه‌های قبلی فرانت‌اند
    image = serializers.SerializerMethodField()
    image_mobile = serializers.SerializerMethodField()

    class Meta:
        model = TopBanner
        fields = (
            'id', 'link_url', 'alt_text', 'fit_mode', 'background_color',
            'display_height_desktop', 'display_height_mobile',
            'desktop', 'mobile', 'image', 'image_mobile',
        )

    def _url(self, field):
        if not field:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(field.url) if request else field.url

    def get_desktop(self, obj):
        return {
            'webp': self._url(obj.desktop_webp),
            'jpeg': self._url(obj.desktop_jpeg),
            'width': obj.desktop_width,
            'height': obj.desktop_height,
        }

    def get_mobile(self, obj):
        return {
            'webp': self._url(obj.mobile_webp),
            'jpeg': self._url(obj.mobile_jpeg),
            'width': obj.mobile_width,
            'height': obj.mobile_height,
        }

    def get_image(self, obj):
        return self._url(obj.desktop_jpeg) or self._url(obj.image)

    def get_image_mobile(self, obj):
        return self._url(obj.mobile_jpeg)
