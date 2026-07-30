from rest_framework import serializers

from .models import Comment
from .validators import validate_no_links


class CommentSerializer(serializers.ModelSerializer):
    """
    نمایش دیدگاه‌ها زیر مقاله.

    نکته‌ی امنیتی: عمداً نام کاربری واقعی (username، که برای لاگین استفاده
    می‌شود) نمایش داده نمی‌شود؛ به‌جای آن از get_public_name() که یا
    نام نمایشی دلخواه کاربر است یا یک نسخه‌ی نقاب‌دار (مثل «moh***») از
    نام کاربری استفاده می‌شود. این کار از افشای عمومی یوزرنیم‌های معتبر
    سایت (که حمله‌ی brute-force/credential-stuffing را راحت‌تر می‌کند) جلوگیری می‌کند.
    """

    display_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'article', 'display_name', 'avatar', 'parent', 'body', 'created_at', 'is_owner')
        read_only_fields = ('id', 'display_name', 'avatar', 'created_at', 'is_owner')

    def get_display_name(self, obj):
        return obj.user.get_public_name()

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.user.avatar and hasattr(obj.user.avatar, 'url'):
            return request.build_absolute_uri(obj.user.avatar.url) if request else obj.user.avatar.url
        return None

    def get_is_owner(self, obj):
        """آیا کاربر لاگین‌کرده فعلی صاحب همین دیدگاه است (برای نمایش دکمه‌های ویرایش/حذف)."""
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.user_id == request.user.id


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    ثبت دیدگاه جدید. فقط کاربران لاگین‌کرده مجاز به استفاده از این سریالایزر هستند
    (این محدودیت در permission_classes ویو اعمال می‌شود). کاربر از request.user
    گرفته می‌شود، نه از بدنه درخواست.
    """

    class Meta:
        model = Comment
        fields = ('id', 'article', 'parent', 'body')

    def validate_body(self, value):
        return validate_no_links(value)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    """ویرایش دیدگاه؛ فقط متن دیدگاه قابل تغییر است (نه مقاله یا کاربر)."""

    class Meta:
        model = Comment
        fields = ('id', 'body')

    def validate_body(self, value):
        return validate_no_links(value)
