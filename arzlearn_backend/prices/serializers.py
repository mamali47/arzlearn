from rest_framework import serializers

from .models import Price


class PriceSerializer(serializers.ModelSerializer):
    is_positive_change = serializers.BooleanField(read_only=True)

    class Meta:
        model = Price
        fields = (
            'symbol', 'name_fa', 'price_value', 'currency',
            'change_percent', 'is_positive_change', 'updated_at',
        )
