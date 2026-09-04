import logging

from django.core.management import call_command
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Article
from .telegram import post_article_to_telegram

logger = logging.getLogger(__name__)


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


@receiver(post_save, sender=Article)
def regenerate_static_page(sender, instance, **kwargs):
    """
    هر بار مقاله‌ای ذخیره می‌شود (ساخت یا ویرایش)، فایل HTML سئو-فرندلی
    مخصوص همان مقاله دوباره ساخته می‌شود تا همیشه با آخرین تغییرات
    (عنوان، خلاصه، متن، تصویر و ...) هماهنگ بماند.

    اگر مقاله دیگر «منتشر شده» نیست (مثلاً به پیش‌نویس برگردانده شده)، این
    تابع کاری نمی‌کند؛ صفحه‌ی قدیمی همچنان روی دیسک می‌ماند ولی چون از
    sitemap.xml و لینک‌های سایت حذف می‌شود، عملاً کسی به آن نمی‌رسد. اگر
    می‌خواهی همان لحظه هم حذف شود، بعداً می‌توانیم این را اضافه کنیم.

    خطاها فقط لاگ می‌شوند و باعث خطا در ذخیره‌ی مقاله در ادمین نمی‌شوند؛
    چون این کار جانبی (side effect) است، نباید ذخیره‌ی اصلی مقاله را خراب کند.
    """
    if instance.status != 'published':
        return

    try:
        call_command('generate_static_pages', slug=instance.slug)
    except Exception:
        logger.exception('ساخت صفحه‌ی از پیش‌رندرشده برای مقاله «%s» با خطا مواجه شد.', instance.slug)
