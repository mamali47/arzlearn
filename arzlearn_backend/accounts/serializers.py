from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
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


class EmailVerificationConfirmSerializer(serializers.Serializer):
    """
    تایید ایمیل با توکنی که در لینک ارسال‌شده به ایمیل کاربر قرار دارد.
    """

    token = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    درخواست ارسال ایمیل بازیابی رمز عبور.
    """

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    تایید نهایی بازیابی رمز عبور با uid و توکنی که در لینک ایمیل ارسال شده است.
    از django.contrib.auth.tokens.default_token_generator استفاده می‌کند که
    توکن استاندارد و امن خود جنگو است (بعد از تغییر رمز عبور خودکار باطل می‌شود).
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'رمز عبور و تکرار آن یکسان نیستند.'}
            )

        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError('لینک بازیابی رمز عبور نامعتبر است.')

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError(
                'این لینک نامعتبر یا منقضی شده است. لطفاً دوباره درخواست بازیابی رمز عبور بدهید.'
            )

        try:
            validate_password(attrs['new_password'], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'new_password': list(exc.messages)})

        attrs['user'] = user
        return attrs
