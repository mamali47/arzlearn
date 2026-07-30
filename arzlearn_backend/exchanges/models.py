from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Exchange(models.Model):
    """
    صرافی‌های معتبر برای سکشن «بهترین صرافی‌ها» در صفحه اصلی.
    کاملاً از طریق ادمین جنگو مدیریت می‌شود.
    """

    name = models.CharField(max_length=100, verbose_name='نام صرافی')
    logo = models.ImageField(upload_to='exchanges/', verbose_name='لوگو')
    maker_fee = models.CharField(
        max_length=20,
        verbose_name='کارمزد میکر',
        help_text='مثلاً: 0.1%',
    )
    taker_fee = models.CharField(
        max_length=20,
        verbose_name='کارمزد تیکر',
        help_text='مثلاً: 0.2%',
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='امتیاز (از ۵)',
        help_text='عدد اعشاری بین ۰ تا ۵ (مثلاً 4.5)',
    )
    short_description = models.CharField(
        max_length=200, verbose_name='توضیحات کوتاه'
    )
    registration_url = models.URLField(verbose_name='لینک ثبت‌نام')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'صرافی'
        verbose_name_plural = 'صرافی‌ها'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
