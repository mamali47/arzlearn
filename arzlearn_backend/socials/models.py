from django.db import models


class SocialLink(models.Model):
    """
    آیتم‌های بخش «ارزلرن در شبکه‌های اجتماعی» در فوتر سایت.
    کاملاً از طریق ادمین جنگو قابل اضافه/ویرایش/حذف است.
    """

    platform_name = models.CharField(
        max_length=50, verbose_name='نام شبکه اجتماعی',
        help_text='مثلاً: تلگرام، اینستاگرام، توییتر (X)',
    )
    icon = models.ImageField(upload_to='socials/', verbose_name='آیکون/لوگو')
    url = models.URLField(verbose_name='لینک کانال/صفحه')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'شبکه اجتماعی'
        verbose_name_plural = 'شبکه‌های اجتماعی'
        ordering = ['order']

    def __str__(self):
        return self.platform_name
