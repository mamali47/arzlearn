from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import CustomUser
from .validators import english_username_validator


class UserSerializer(serializers.ModelSerializer):
    """اطلاعات عمومی کاربر (برای نمایش در هدر و پروفایل)."""

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'display_name', 'email', 'avatar', 'is_email_verified', 'date_joined')
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """
    سریالایزر ثبت‌نام. قوانین:
    - نام کاربری فقط انگلیسی
    - ایمیل معتبر و یکتا
    - رمز عبور شامل حرف بزرگ، حرف کوچک، عدد و حداقل ۸ کاراکتر
    - رمز عبور و تکرار آن باید برابر باشند
    """

    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'display_name', 'email', 'password', 'password_confirm')

    def validate_username(self, value):
        english_username_validator(value)
        if CustomUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('این نام کاربری قبلاً استفاده شده است.')
        return value

    def validate_display_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('نام نمایشی نمی‌تواند خالی باشد.')
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if password != password_confirm:
            raise serializers.ValidationError(
                {'password_confirm': 'رمز عبور و تکرار آن یکسان نیستند.'}
            )

        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    ورود با نام کاربری یا ایمیل + رمز عبور.
    """

    identifier = serializers.CharField(help_text='نام کاربری یا ایمیل')
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        user = None
        try:
            user_obj = CustomUser.objects.get(email__iexact=identifier)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            username = identifier

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError('نام کاربری/ایمیل یا رمز عبور اشتباه است.')
        if not user.is_active:
            raise serializers.ValidationError('این حساب کاربری غیرفعال است.')

        attrs['user'] = user
        return attrs
