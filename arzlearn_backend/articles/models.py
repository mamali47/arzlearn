import math
import re

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from django_ckeditor_5.fields import CKEditor5Field

from .sanitize import sanitize_article_html


class Category(models.Model):
    """
    دسته‌بندی مقالات - می‌تواند مادر یا فرزند یک دسته‌بندی دیگر باشد.
    این مدل کاملاً از طریق ادمین جنگو مدیریت می‌شود و منوی هدر سایت
    از روی همین داده‌ها ساخته می‌شود.
    """

    name = models.CharField(max_length=100, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(
        max_length=150, unique=True, allow_unicode=True, blank=True,
        verbose_name='نامک (Slug)',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='دسته‌بندی مادر',
        help_text='در صورتی که این دسته‌بندی زیرمجموعه یک دسته‌بندی دیگر است انتخاب کنید.',
    )
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name

    def get_self_and_descendant_ids(self):
        """
        شناسه خود دسته‌بندی + تمام زیردسته‌های مستقیم آن (چون حداکثر یک سطح
        تودرتو مجاز است). برای این استفاده می‌شود که وقتی دسته‌بندی مادر
        (مثل «اخبار») نمایش داده می‌شود، مقالات زیردسته‌هایش (مثل «اخبار
        بیت‌کوین») هم در آن دیده شوند.
        """
        ids = [self.id]
        ids.extend(self.children.filter(is_active=True).values_list('id', flat=True))
        return ids

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def clean(self):
        if self.parent and self.parent_id == self.id:
            raise ValidationError('دسته‌بندی نمی‌تواند والد خودش باشد.')
        if self.parent and self.parent.parent_id is not None:
            raise ValidationError(
                'حداکثر یک سطح تو در تو برای دسته‌بندی مجاز است '
                '(دسته‌بندی فرزند نمی‌تواند خودش والد داشته باشد).'
            )


class Tag(models.Model):
    """تگ‌های مقالات - تماماً در ادمین جنگو ساخته می‌شوند."""

    name = models.CharField(max_length=60, unique=True, verbose_name='نام تگ')
    slug = models.SlugField(
        max_length=80, unique=True, allow_unicode=True, blank=True, verbose_name='نامک'
    )

    class Meta:
        verbose_name = 'تگ'
        verbose_name_plural = 'تگ‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Article(models.Model):
    """مدل مقاله؛ فقط از طریق ادمین جنگو ساخته و ویرایش می‌شود."""

    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
    )

    title = models.CharField(max_length=250, verbose_name='تایتل مقاله')
    slug = models.SlugField(
        max_length=280, unique=True, allow_unicode=True, blank=True, verbose_name='نامک'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='articles',
        verbose_name='دسته‌بندی',
    )

    main_tags = models.ManyToManyField(
        Tag, related_name='main_articles', blank=True,
        verbose_name='سه تگ اصلی',
        help_text='دقیقاً باید ۳ تگ اصلی برای هر مقاله انتخاب شود.',
    )
    secondary_tags = models.ManyToManyField(
        Tag, related_name='secondary_articles', blank=True,
        verbose_name='تگ‌های فرعی',
    )

    image = models.ImageField(upload_to='articles/%Y/%m/', verbose_name='تصویر مقاله')
    summary = models.TextField(max_length=500, verbose_name='خلاصه مقاله')
    body = CKEditor5Field('متن مقاله', config_name='default')

    reading_time_minutes = models.PositiveIntegerField(
        blank=True, null=True, verbose_name='مدت زمان مطالعه (دقیقه)',
        help_text='در صورت خالی گذاشتن، بصورت خودکار محاسبه می‌شود.',
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='articles', verbose_name='نویسنده',
    )

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='published', verbose_name='وضعیت'
    )
    published_at = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    views_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')

    is_posted_to_telegram = models.BooleanField(
        default=False, editable=False, verbose_name='در تلگرام پست شده',
    )

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        if self.body:
            self.body = sanitize_article_html(self.body)

        if not self.reading_time_minutes:
            self.reading_time_minutes = self._calculate_reading_time()

        super().save(*args, **kwargs)

    def _calculate_reading_time(self):
        """محاسبه تقریبی زمان مطالعه بر اساس تعداد کلمات متن (حذف تگ‌های HTML)."""
        plain_text = re.sub(r'<[^>]+>', ' ', self.body or '')
        word_count = len(plain_text.split())
        words_per_minute = 150
        minutes = math.ceil(word_count / words_per_minute) if word_count else 1
        return max(minutes, 1)


class ArticleFAQ(models.Model):
    """
    سوالات متداول (FAQ) هر مقاله؛ در پایین صفحه‌ی مقاله به‌صورت آکاردئون
    (کلیک برای دیدن جواب) نمایش داده می‌شوند. علاوه بر کمک به خواننده، این
    سوال‌وجواب‌ها به‌صورت Schema.org (FAQPage) هم به گوگل داده می‌شوند که
    می‌تواند باعث نمایش پاسخ مستقیم در نتایج جستجو (rich snippet) شود.
    """

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='faqs', verbose_name='مقاله'
    )
    question = models.CharField(max_length=300, verbose_name='سوال')
    answer = models.TextField(verbose_name='پاسخ')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question
