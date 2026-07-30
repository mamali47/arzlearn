from django.conf import settings
from django.db import models

from articles.models import Article


class Comment(models.Model):
    """
    دیدگاه کاربران روی مقالات.
    فقط کاربران ثبت‌نام‌کرده (لاگین کرده) امکان ثبت دیدگاه دارند؛
    این محدودیت در لایه API/ویو (فاز ۲) اعمال می‌شود.
    """

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments', verbose_name='مقاله'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments',
        verbose_name='کاربر',
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies', verbose_name='پاسخ به دیدگاه',
    )
    body = models.TextField(max_length=1000, verbose_name='متن دیدگاه')
    is_approved = models.BooleanField(
        default=True, verbose_name='تایید شده',
        help_text='در صورت نیاز به بررسی قبل از نمایش، غیرفعال کنید.',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'دیدگاه'
        verbose_name_plural = 'دیدگاه‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.article.title[:30]}'
