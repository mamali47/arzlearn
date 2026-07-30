from rest_framework import serializers

from .models import Exchange


class ExchangeSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Exchange
        fields = ('id', 'name', 'logo', 'maker_fee', 'taker_fee', 'rating', 'short_description', 'registration_url', 'order')

    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url
        return None
