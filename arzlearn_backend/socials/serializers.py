from rest_framework import serializers

from .models import SocialLink


class SocialLinkSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = SocialLink
        fields = ('id', 'platform_name', 'icon', 'url', 'order')

    def get_icon(self, obj):
        request = self.context.get('request')
        if obj.icon and hasattr(obj.icon, 'url'):
            return request.build_absolute_uri(obj.icon.url) if request else obj.icon.url
        return None
