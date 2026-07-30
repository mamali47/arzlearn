from django.db import models


class TopBanner(models.Model):
    """
    بنر تبلیغاتی/اطلاع‌رسانی بالای هدر سایت (بالاترین قسمت صفحه).
    فقط یک بنر «فعال» در هر لحظه نمایش داده می‌شود. اگر هیچ بنر فعالی
    وجود نداشته باشد، این قسمت اصلاً در سایت نمایش داده نمی‌شود.
    """

    image = models.ImageField(upload_to='banners/', verbose_name='تصویر بنر')
    link_url = models.URLField(verbose_name='لینک مقصد (وقتی کاربر روی بنر کلیک کند)')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'بنر بالای سایت'
        verbose_name_plural = 'بنرهای بالای سایت'
        ordering = ['-created_at']

    def __str__(self):
        return f'بنر #{self.pk} ({"فعال" if self.is_active else "غیرفعال"})'
