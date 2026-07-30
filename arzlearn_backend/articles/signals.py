from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Article
from .telegram import post_article_to_telegram


@receiver(post_save, sender=Article)
def send_new_article_to_telegram(sender, instance, created, **kwargs):
    """
    هر بار که یک مقاله ذخیره می‌شود (چه ساخت جدید، چه ویرایش)، اگر وضعیت آن
    «منتشر شده» باشد و قبلاً به تلگرام ارسال نشده باشد، فوراً پست می‌شود.
    از Article.objects.filter(...).update() به‌جای article.save() استفاده
    می‌کنیم تا سیگنال post_save دوباره اجرا نشود (از حلقه‌ی بی‌نهایت جلوگیری می‌شود).
    """
    if instance.status != 'published' or instance.is_posted_to_telegram:
        return

    success = post_article_to_telegram(instance)
    if success:
        Article.objects.filter(pk=instance.pk).update(is_posted_to_telegram=True)
