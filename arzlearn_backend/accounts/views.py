from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .emails import send_password_reset_email, send_verification_email
from .models import CustomUser
from .serializers import (
    EmailVerificationConfirmSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .tokens import make_pending_registration_token, read_pending_registration_token


class RegisterAPIView(APIView):
    """
    POST /api/accounts/register/
    body: { "username": "...", "display_name": "...", "email": "...", "password": "...", "password_confirm": "..." }

    مهم: این مرحله هیچ کاربری در دیتابیس نمی‌سازد! فقط اطلاعات را اعتبارسنجی
    می‌کند، هش رمز عبور را داخل یک توکن امضاشده جا می‌دهد و برایش یک ایمیل
    تایید می‌فرستد. کاربر فقط وقتی روی لینک ایمیلش کلیک کند (VerifyEmailAPIView)
    واقعاً در دیتابیس ساخته می‌شود. اگر هیچ‌وقت لینک را نزند، هیچ اکانتی
    برایش باقی نمی‌ماند.
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = 'register'

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payload = {
            'username': data['username'],
            'display_name': data['display_name'],
            'email': data['email'],
            'password_hash': make_password(data['password']),
        }
        token = make_pending_registration_token(payload)
        send_verification_email(email=data['email'], display_name=data['display_name'], token=token)

        return Response(
            {
                'detail': (
                    'یک ایمیل تایید برایتان ارسال شد. برای تکمیل ثبت‌نام، '
                    'روی لینک داخل ایمیل کلیک کنید.'
                )
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """
    POST /api/accounts/login/
    body: { "identifier": "username-or-email", "password": "..." }
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = 'login'

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })


class LogoutAPIView(APIView):
    """
    POST /api/accounts/logout/  (نیاز به هدر Authorization: Token <token>)
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'با موفقیت خارج شدید.'}, status=status.HTTP_200_OK)


class MeAPIView(generics.RetrieveAPIView):
    """
    GET /api/accounts/me/  (نیاز به هدر Authorization: Token <token>)
    برای نمایش نام کاربری در هدر بعد از ورود.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailAPIView(APIView):
    """
    POST /api/accounts/verify-email/
    body: { "token": "..." }

    اینجاست که کاربر واقعاً در دیتابیس ساخته می‌شود. بعد از ساخت، برای
    تجربه‌ی بهتر، بلافاصله یک توکن ورود هم برمی‌گردانیم تا کاربر خودکار
    لاگین شود (نیازی نیست دوباره با رمز عبورش وارد شود).
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        payload = read_pending_registration_token(token)
        if payload is None:
            return Response(
                {'detail': 'این لینک نامعتبر یا منقضی شده است. لطفاً دوباره ثبت‌نام کنید.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = payload.get('username')
        email = payload.get('email')

        # جلوگیری از تداخل: بررسی دوباره که در فاصله‌ی بین ثبت‌نام و تایید،
        # شخص دیگری همین نام‌کاربری/ایمیل را (با تایید ایمیل خودش) نگرفته باشد.
        if CustomUser.objects.filter(username__iexact=username).exists():
            return Response(
                {'detail': 'این نام کاربری در همین حین توسط شخص دیگری ثبت شده است. لطفاً دوباره ثبت‌نام کنید.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if CustomUser.objects.filter(email__iexact=email).exists():
            return Response(
                {'detail': 'این ایمیل در همین حین توسط شخص دیگری ثبت شده است. لطفاً دوباره ثبت‌نام کنید.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser(
            username=username,
            display_name=payload.get('display_name', ''),
            email=email,
            is_email_verified=True,
        )
        user.password = payload['password_hash']  # از قبل با make_password هش شده
        user.save()

        auth_token, _created = Token.objects.get_or_create(user=user)

        return Response({
            'token': auth_token.key,
            'user': UserSerializer(user).data,
        })


class PasswordResetRequestAPIView(APIView):
    """
    POST /api/accounts/password-reset/
    body: { "email": "..." }
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email__iexact=email)
        except CustomUser.DoesNotExist:
            user = None

        if user is not None:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_password_reset_email(user, uid, token)

        # پیام همیشه یکسان است، حتی اگر ایمیل در سایت ثبت نشده باشد؛
        # این کار از افشای اینکه چه ایمیل‌هایی در سایت ثبت‌نام کرده‌اند جلوگیری می‌کند.
        return Response(
            {'detail': 'اگر این ایمیل در سایت ثبت شده باشد، لینک بازیابی رمز عبور برایش ارسال شد.'}
        )


class PasswordResetConfirmAPIView(APIView):
    """
    POST /api/accounts/password-reset-confirm/
    body: { "uid": "...", "token": "...", "new_password": "...", "new_password_confirm": "..." }
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])

        # همه‌ی نشست‌های ورود قبلی باطل می‌شوند (برای امنیت، اگر رمز قبلی لو رفته بود)
        Token.objects.filter(user=user).delete()

        return Response({'detail': 'رمز عبور با موفقیت تغییر کرد.'})
