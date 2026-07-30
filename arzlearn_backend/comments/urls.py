from django.urls import path

from .views import CommentDetailAPIView, CommentListCreateAPIView

app_name = 'comments'

urlpatterns = [
    path('', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
]
