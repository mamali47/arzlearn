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
from .tokens import make_email_verification_token, read_email_verification_token


class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/accounts/register/
    body: { "username": "...", "email": "...", "password": "...", "password_confirm": "..." }
    """

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'register'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _created = Token.objects.get_or_create(user=user)

        # بلافاصله بعد از ثبت‌نام یک ایمیل تایید برای کاربر ارسال می‌شود
        verification_token = make_email_verification_token(user)
        send_verification_email(user, verification_token)

        return Response(
            {
                'token': token.key,
                'user': UserSerializer(user).data,
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


class ResendVerificationEmailAPIView(APIView):
    """
    POST /api/accounts/resend-verification/  (نیاز به هدر Authorization: Token <token>)
    برای وقتی که کاربر ایمیل اولش را گم کرده یا منقضی شده است.
    """

    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = 'email_verification'

    def post(self, request):
        user = request.user
        if user.is_email_verified:
            return Response(
                {'detail': 'ایمیل شما قبلاً تایید شده است.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = make_email_verification_token(user)
        send_verification_email(user, token)
        return Response({'detail': 'ایمیل تایید دوباره ارسال شد.'})


class VerifyEmailAPIView(APIView):
    """
    POST /api/accounts/verify-email/
    body: { "token": "..." }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        user_id = read_email_verification_token(token)
        if user_id is None:
            return Response(
                {'detail': 'این لینک نامعتبر یا منقضی شده است.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'لینک نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return Response({'detail': 'ایمیل با موفقیت تایید شد.'})


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
