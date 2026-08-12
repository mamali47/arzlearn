from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    url = models.URLField()

    # نسخه دسکتاپ - همین که الان داری
    image_desktop = models.ImageField(
        upload_to="banners/desktop/",
        verbose_name="بنر دسکتاپ"
    )

    # نسخه موبایل - اختیاری؛ اگه خالی بود از دسکتاپ استفاده میشه
    image_mobile = models.ImageField(
        upload_to="banners/mobile/",
        blank=True,
        null=True,
        verbose_name="بنر موبایل (اختیاری)"
    )

    alt_text = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "بنر تبلیغاتی"
        verbose_name_plural = "بنرهای تبلیغاتی"

    def __str__(self):
        return self.title or f"بنر #{self.pk}"
