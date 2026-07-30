from django.urls import path

from .views import ActiveTopBannerAPIView

app_name = 'topbanner'

urlpatterns = [
    path('active/', ActiveTopBannerAPIView.as_view(), name='active'),
]
