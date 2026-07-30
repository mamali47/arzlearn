from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Comment
from .permissions import IsCommentOwner
from .serializers import CommentCreateSerializer, CommentSerializer, CommentUpdateSerializer


class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/comments/?article=<slug>   -> لیست دیدگاه‌های تاییدشده یک مقاله
    POST /api/comments/                  -> ثبت دیدگاه جدید (فقط کاربر لاگین‌کرده)
         body: { "article": <id>, "body": "...", "parent": <id یا null> }
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.filter(is_approved=True).select_related('user', 'article')
        article_slug = self.request.query_params.get('article')
        if article_slug:
            queryset = queryset.filter(article__slug=article_slug)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        """
        بعد از ثبت موفق، دیدگاه را با CommentSerializer کامل (شامل username،
        avatar و is_owner) برمی‌گردانیم، نه با CommentCreateSerializer که این
        فیلدها را ندارد؛ در غیر این صورت فرانت‌اند موقع نمایش دیدگاه تازه
        ثبت‌شده با خطا مواجه می‌شود (چون username آن undefined است).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        output_serializer = CommentSerializer(comment, context=self.get_serializer_context())
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=201, headers=headers)


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/comments/<id>/  -> جزئیات یک دیدگاه
    PATCH  /api/comments/<id>/  -> ویرایش متن دیدگاه (فقط صاحب دیدگاه)
    DELETE /api/comments/<id>/  -> حذف دیدگاه (فقط صاحب دیدگاه)
    """

    queryset = Comment.objects.select_related('user', 'article')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwner]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return CommentUpdateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def update(self, request, *args, **kwargs):
        """بعد از ویرایش، دیدگاه کامل (با username/avatar/is_owner) برگردانده می‌شود."""
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        output_serializer = CommentSerializer(comment, context=self.get_serializer_context())
        return Response(output_serializer.data)
