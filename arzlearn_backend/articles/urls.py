from django.urls import path

from .views import (
    ArticleDetailAPIView,
    ArticleSearchAPIView,
    CategoryArticlesAPIView,
    CategoryListAPIView,
    LatestAnalysisAPIView,
    LatestNewsAPIView,
)

app_name = 'articles'

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<str:slug>/', CategoryArticlesAPIView.as_view(), name='category-articles'),
    path('latest-news/', LatestNewsAPIView.as_view(), name='latest-news'),
    path('latest-analysis/', LatestAnalysisAPIView.as_view(), name='latest-analysis'),
    path('search/', ArticleSearchAPIView.as_view(), name='search'),
    # این مسیر باید آخرین مورد باشد چون <str:slug> هر رشته‌ای را می‌گیرد
    path('<str:slug>/', ArticleDetailAPIView.as_view(), name='article-detail'),
]
