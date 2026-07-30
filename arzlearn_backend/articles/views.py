from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Article, Category
from .serializers import ArticleDetailSerializer, ArticleListSerializer, CategorySerializer

# نام دسته‌بندی‌هایی که سکشن‌های ثابت صفحه اصلی (آخرین اخبار / آخرین تحلیل‌ها)
# بر اساس آن‌ها پر می‌شوند. این دسته‌بندی‌ها باید در ادمین جنگو با همین نام ساخته شوند.
NEWS_CATEGORY_NAME = 'اخبار'
ANALYSIS_CATEGORY_NAME = 'تحلیل'


def _get_category_or_none(name):
    return Category.objects.filter(name__iexact=name, is_active=True).first()


class CategoryListAPIView(generics.ListAPIView):
    """
    GET /api/articles/categories/
    لیست دسته‌بندی‌های مادر (با زیردسته‌ها) برای منوی هدر.
    """

    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Category.objects.filter(parent__isnull=True, is_active=True)
            .order_by('order', 'name')
        )


class CategoryArticlesAPIView(generics.ListAPIView):
    """
    GET /api/articles/categories/<slug>/
    لیست مقالات یک دسته‌بندی (صفحه اختصاصی دسته‌بندی، مثل صفحه اخبار).

    نکته مهم: اگر این دسته‌بندی زیردسته‌هایی داشته باشد (مثلاً «اخبار» که
    زیردسته‌ی «اخبار بیت‌کوین» را دارد)، مقالات ثبت‌شده در آن زیردسته‌ها هم
    اینجا نمایش داده می‌شوند، نه فقط مقالاتی که مستقیماً روی خود دسته‌بندی
    مادر ثبت شده‌اند.
    """

    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        category_ids = category.get_self_and_descendant_ids()
        return (
            Article.objects.filter(category_id__in=category_ids, status='published')
            .select_related('category')
            .prefetch_related('main_tags')
            .order_by('-published_at')
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        response.data['category'] = CategorySerializer(category, context={'request': request}).data
        return response


class LatestNewsAPIView(generics.ListAPIView):
    """
    GET /api/articles/latest-news/
    سکشن هیرو صفحه اصلی: ۳ آخرین مقاله دسته‌بندی «اخبار» (به‌همراه زیردسته‌هایش).
    """

    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        category = _get_category_or_none(NEWS_CATEGORY_NAME)
        if not category:
            return Article.objects.none()
        category_ids = category.get_self_and_descendant_ids()
        return (
            Article.objects.filter(category_id__in=category_ids, status='published')
            .select_related('category')
            .prefetch_related('main_tags')
            .order_by('-published_at')[:3]
        )


class LatestAnalysisAPIView(generics.ListAPIView):
    """
    GET /api/articles/latest-analysis/
    سکشن آخرین تحلیل‌ها در صفحه اصلی: ۴ آخرین مقاله دسته‌بندی «تحلیل» (به‌همراه زیردسته‌هایش).
    """

    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        category = _get_category_or_none(ANALYSIS_CATEGORY_NAME)
        if not category:
            return Article.objects.none()
        category_ids = category.get_self_and_descendant_ids()
        return (
            Article.objects.filter(category_id__in=category_ids, status='published')
            .select_related('category')
            .prefetch_related('main_tags')
            .order_by('-published_at')[:4]
        )


class ArticleSearchAPIView(generics.ListAPIView):
    """
    GET /api/articles/search/?q=کلمه
    جستجو در تایتل و بدنه مقالات.
    """

    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        if not query:
            return Article.objects.none()
        return (
            Article.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query),
                status='published',
            )
            .select_related('category')
            .prefetch_related('main_tags')
            .distinct()
            .order_by('-published_at')
        )


class ArticleDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/articles/<slug>/
    صفحه اختصاصی مقاله؛ هر بار مشاهده، تعداد بازدید یک واحد افزایش می‌یابد.
    """

    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Article.objects.filter(status='published')
            .select_related('category', 'author')
            .prefetch_related('main_tags', 'secondary_tags', 'faqs')
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Article.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
