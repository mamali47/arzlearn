from django.db import models


class Price(models.Model):
    """
    نگهداری آخرین قیمت هر دارایی. هر ردیف با سرویس اسکرپینگ (services.py)
    بصورت مداوم بروزرسانی می‌شود. کاربر همیشه فقط آخرین ردیف هر symbol
    را می‌بیند (بروزرسانی جای‌گزین، نه افزودن ردیف جدید).
    """

    CURRENCY_CHOICES = (
        ('USD', 'دلار'),
        ('IRR', 'ریال'),
    )

    SYMBOL_CHOICES = (
        ('BTC', 'بیت کوین'),
        ('ETH', 'اتریوم'),
        ('SOL', 'سولانا'),
        ('BNB', 'بایننس کوین'),
        ('HYPE', 'هایپرلیکوئید'),
        ('XAUT', 'طلا (تتر گلد)'),
        ('USD', 'دلار'),
        ('GOLD18', 'طلای ۱۸ عیار'),
    )

    symbol = models.CharField(
        max_length=10, choices=SYMBOL_CHOICES, unique=True, verbose_name='نماد'
    )
    name_fa = models.CharField(max_length=50, verbose_name='نام فارسی')
    price_value = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name='قیمت'
    )
    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, verbose_name='واحد پول'
    )
    change_percent = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, verbose_name='درصد تغییر'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'قیمت'
        verbose_name_plural = 'قیمت‌ها'
        ordering = ['symbol']

    def __str__(self):
        return f'{self.name_fa}: {self.price_value} {self.currency}'

    @property
    def is_positive_change(self):
        return self.change_percent >= 0
