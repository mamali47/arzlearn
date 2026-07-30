from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


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
