from rest_framework import serializers
from .models import TopBanner

class TopBannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_mobile = serializers.SerializerMethodField()

    class Meta:
        model = TopBanner
        fields = ('id', 'image', 'image_mobile', 'link_url')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_image_mobile(self, obj):
        request = self.context.get('request')
        if obj.image_mobile and hasattr(obj.image_mobile, 'url'):
            return request.build_absolute_uri(obj.image_mobile.url) if request else obj.image_mobile.url
        return None
