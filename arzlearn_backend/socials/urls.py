from django.urls import path

from .views import SocialLinkListAPIView

app_name = 'socials'

urlpatterns = [
    path('', SocialLinkListAPIView.as_view(), name='social-list'),
]
