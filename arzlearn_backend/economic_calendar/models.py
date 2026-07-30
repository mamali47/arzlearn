from django.db import models


class EconomicEvent(models.Model):
    """
    رویداد تقویم اقتصادی (مثل NFP، نرخ بهره، تورم و...).
    این داده‌ها هر هفته بصورت خودکار از یک API خارجی گرفته می‌شوند
    (management command: update_economic_calendar) اما امکان افزودن/ویرایش
    دستی از ادمین جنگو هم وجود دارد (مثلاً اگر API موقتاً در دسترس نبود).
    """

    IMPORTANCE_CHOICES = (
        ('high', 'بسیار مهم (قرمز)'),
        ('medium', 'مهم (نارنجی)'),
        ('low', 'کم‌اهمیت (زرد)'),
    )

    title = models.CharField(max_length=200, verbose_name='عنوان رویداد')
    country = models.CharField(max_length=10, verbose_name='کشور/ارز', help_text='مثلاً USD، EUR')
    importance = models.CharField(
        max_length=10, choices=IMPORTANCE_CHOICES, verbose_name='اهمیت'
    )
    event_date = models.DateField(verbose_name='تاریخ (میلادی)')
    event_time = models.TimeField(null=True, blank=True, verbose_name='ساعت')

    actual = models.CharField(max_length=30, blank=True, verbose_name='مقدار واقعی')
    forecast = models.CharField(max_length=30, blank=True, verbose_name='پیش‌بینی')
    previous = models.CharField(max_length=30, blank=True, verbose_name='مقدار قبلی')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'رویداد اقتصادی'
        verbose_name_plural = 'رویدادهای اقتصادی'
        ordering = ['event_date', 'event_time']

    def __str__(self):
        return f'{self.title} ({self.country}) - {self.event_date}'
