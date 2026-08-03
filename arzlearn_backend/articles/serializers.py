from rest_framework import serializers
from django.conf import settings

from .models import Article, ArticleFAQ, Category, Tag


class ArticleFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleFAQ
        fields = ('id', 'question', 'answer')


class CategorySerializer(serializers.ModelSerializer):
    """
    سریالایزر دسته‌بندی برای منوی هدر (شامل زیردسته‌ها).
    """

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'order', 'children')

    def get_children(self, obj):
        active_children = obj.children.filter(is_active=True).order_by('order', 'name')
        return CategorySerializer(active_children, many=True, context=self.context).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class CategoryMiniSerializer(serializers.ModelSerializer):
    """نسخه خلاصه دسته‌بندی، برای استفاده داخل کارت مقاله و breadcrumb."""

    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent')

    def get_parent(self, obj):
        if obj.parent:
            return {'id': obj.parent.id, 'name': obj.parent.name, 'slug': obj.parent.slug}
        return None


class ArticleListSerializer(serializers.ModelSerializer):
    """
    نسخه خلاصه مقاله؛ برای لیست‌ها (آخرین اخبار، آخرین تحلیل‌ها، صفحه دسته‌بندی، جستجو).
    """

    category = CategoryMiniSerializer(read_only=True)
    main_tags = TagSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'slug', 'image', 'summary', 'category',
            'main_tags', 'published_at', 'reading_time_minutes',
        )

    def get_image(self, obj):
    	request = self.context.get('request')
    	if obj.image and hasattr(obj.image, 'url'):
        	return request.build_absolute_uri(obj.image.url) if request else obj.image.url
    	return None


class ArticleDetailSerializer(ArticleListSerializer):
    """
    نسخه کامل مقاله برای صفحه اختصاصی مقاله؛ شامل متن کامل و مطالب مشابه.
    """

    secondary_tags = TagSerializer(many=True, read_only=True)
    author_username = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()
    faqs = ArticleFAQSerializer(many=True, read_only=True)

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + (
            'body', 'secondary_tags', 'author_username', 'views_count', 'related_articles', 'faqs',
        )

    def get_author_username(self, obj):
        """
        نام نویسنده که در سایت نمایش داده می‌شود؛ عمداً نام کاربری واقعی
        (که برای لاگین به ادمین استفاده می‌شود) نمایش داده نمی‌شود.
        """
        return obj.author.get_public_name() if obj.author else None

    def get_related_articles(self, obj):
        main_tag_ids = obj.main_tags.values_list('id', flat=True)
        related_qs = (
            Article.objects.filter(
                main_tags__in=main_tag_ids, status='published'
            )
            .exclude(id=obj.id)
            .distinct()
            .order_by('-published_at')[:4]
        )
        return ArticleListSerializer(related_qs, many=True, context=self.context).data
