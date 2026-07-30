from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import english_username_validator


class CustomUser(AbstractUser):
    """
    مدل کاربر سفارشی ارزلرن.
    - نام کاربری فقط انگلیسی
    - ایمیل الزامی و یکتا (توسط جنگو اعتبارسنجی می‌شود)
    """

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[english_username_validator],
        error_messages={
            'unique': 'این نام کاربری قبلاً استفاده شده است.',
        },
        verbose_name='نام کاربری',
        help_text='فقط حروف انگلیسی، اعداد، نقطه و آندرلاین مجاز است.',
    )
    email = models.EmailField(
        unique=True,
        verbose_name='ایمیل',
        error_messages={
            'unique': 'این ایمیل قبلاً ثبت شده است.',
        },
    )
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name='تصویر پروفایل'
    )
    display_name = models.CharField(
        max_length=50, blank=True, verbose_name='نام نمایشی',
        help_text=(
            'این نام (نه نام کاربری لاگین) زیر دیدگاه‌ها و در سایت عمومی نمایش داده می‌شود. '
            'اگر خالی بماند، به‌جای آن یک نسخه‌ی نقاب‌دار از نام کاربری نمایش داده می‌شود '
            '(مثلاً «moh***» به‌جای نام کاربری کامل) تا نام کاربری واقعی (که برای ورود '
            'استفاده می‌شود) در معرض دید عمومی قرار نگیرد.'
        ),
    )
    is_email_verified = models.BooleanField(default=False, verbose_name='ایمیل تایید شده')

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.username

    def get_public_name(self):
        """
        نامی که در جاهای عمومی سایت (مثل زیر دیدگاه‌ها) نمایش داده می‌شود.
        عمداً نام کاربری واقعی (که برای لاگین استفاده می‌شود) نمایش داده
        نمی‌شود، چون افشای آن، حدس‌زدن/حمله‌ی brute-force به حساب‌ها را
        برای مهاجم راحت‌تر می‌کند.
        """
        if self.display_name:
            return self.display_name
        if len(self.username) <= 3:
            return self.username[0] + '***'
        return self.username[:3] + '***'
