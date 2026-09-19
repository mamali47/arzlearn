from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .imaging import (
    DESKTOP_REFERENCE_WIDTH,
    DESKTOP_SCALE,
    MOBILE_REFERENCE_WIDTH,
    MOBILE_SCALE,
    render_variant,
    variant_filename,
)

FIT_CHOICES = (
    ('cover', 'پر کردن کامل نوار (ممکن است کمی از لبه‌ها بریده شود)'),
    ('contain', 'نمایش کل بنر بدون برش (دو طرف با رنگ بنر پر می‌شود)'),
)

FOCUS_CHOICES = (
    ('center', 'وسط'),
    ('right', 'راست'),
    ('left', 'چپ'),
)


class TopBanner(models.Model):
    """
    بنر تبلیغاتی/اطلاع‌رسانی بالای هدر سایت.

    فقط کافی است یک تصویر آپلود کنی؛ خود سیستم موقع ذخیره، نسخه‌ی دسکتاپ و
    نسخه‌ی موبایل را با ابعاد استاندارد و فرمت WebP می‌سازد. دیگر لازم نیست
    تصویر را دستی ریسایز کنی و بنر روی موبایل هم ریز دیده نمی‌شود.
    """

    # ---------------------------------------------------------------- ورودی
    image = models.ImageField(
        upload_to='banners/source/',
        verbose_name='تصویر بنر',
        help_text='هر ابعادی مجاز است؛ پیشنهاد حداقل ۲۴۸۰ پیکسل عرض. '
                  'نسخه‌ی دسکتاپ و موبایل خودکار ساخته می‌شود.',
    )
    image_mobile = models.ImageField(
        upload_to='banners/source/mobile/',
        blank=True,
        null=True,
        verbose_name='تصویر مخصوص موبایل (اختیاری)',
        help_text='فقط اگر می‌خواهی روی گوشی طرح کاملاً متفاوتی دیده شود. '
                  'خالی بگذاری، نسخه‌ی موبایل از همان تصویر اصلی ساخته می‌شود.',
    )

    alt_text = models.CharField(
        max_length=125,
        blank=True,
        verbose_name='متن جایگزین تصویر (alt)',
        help_text='توضیح کوتاه محتوای بنر؛ برای سئو و کاربران اسکرین‌ریدر. '
                  'مثال: «جشنواره ثبت‌نام صرافی نوبیتکس».',
    )

    link_url = models.URLField(verbose_name='لینک مقصد (وقتی کاربر روی بنر کلیک کند)')

    # ------------------------------------------------------------- تنظیمات
    display_height_desktop = models.PositiveSmallIntegerField(
        default=92,
        validators=[MinValueValidator(40), MaxValueValidator(220)],
        verbose_name='ارتفاع نوار در دسکتاپ (پیکسل)',
    )
    display_height_mobile = models.PositiveSmallIntegerField(
        default=104,
        validators=[MinValueValidator(40), MaxValueValidator(260)],
        verbose_name='ارتفاع نوار در موبایل (پیکسل)',
    )
    fit_mode = models.CharField(
        max_length=10, choices=FIT_CHOICES, default='cover',
        verbose_name='نحوه جا شدن تصویر',
    )
    focus = models.CharField(
        max_length=10, choices=FOCUS_CHOICES, default='center',
        verbose_name='نقطه مهم تصویر',
        help_text='وقتی حالت «پر کردن کامل» انتخاب شده، این قسمت از تصویر حتماً حفظ می‌شود.',
    )

    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------ خروجی‌های خودکار (فقط‌خواندنی)
    desktop_webp = models.ImageField(upload_to='banners/generated/', blank=True, null=True, editable=False)
    desktop_jpeg = models.ImageField(upload_to='banners/generated/', blank=True, null=True, editable=False)
    desktop_width = models.PositiveIntegerField(default=0, editable=False)
    desktop_height = models.PositiveIntegerField(default=0, editable=False)

    mobile_webp = models.ImageField(upload_to='banners/generated/', blank=True, null=True, editable=False)
    mobile_jpeg = models.ImageField(upload_to='banners/generated/', blank=True, null=True, editable=False)
    mobile_width = models.PositiveIntegerField(default=0, editable=False)
    mobile_height = models.PositiveIntegerField(default=0, editable=False)

    background_color = models.CharField(max_length=7, default='#111318', editable=False)

    # امضای ورودی‌ها؛ تا وقتی عوض نشود تصاویر دوباره ساخته نمی‌شوند.
    render_signature = models.CharField(max_length=255, blank=True, editable=False)

    class Meta:
        verbose_name = 'بنر بالای سایت'
        verbose_name_plural = 'بنرهای بالای سایت'
        ordering = ['-created_at']

    def __str__(self):
        return f'بنر #{self.pk} ({"فعال" if self.is_active else "غیرفعال"})'

    # ------------------------------------------------------------------ منطق
    def _signature(self) -> str:
        return '|'.join([
            str(getattr(self.image, 'name', '')),
            str(getattr(self.image_mobile, 'name', '')),
            str(self.display_height_desktop),
            str(self.display_height_mobile),
            self.fit_mode,
            self.focus,
        ])

    def save(self, *args, **kwargs):
        # اول ذخیره‌ی عادی تا فایل‌های آپلودشده روی دیسک بنشینند.
        super().save(*args, **kwargs)

        if not self.image:
            return

        signature = self._signature()
        if signature == self.render_signature and self.desktop_webp:
            return

        desktop = render_variant(
            self.image,
            reference_width=DESKTOP_REFERENCE_WIDTH,
            scale=DESKTOP_SCALE,
            display_height=self.display_height_desktop,
            fit=self.fit_mode,
            focus=self.focus,
        )
        mobile_source = self.image_mobile if self.image_mobile else self.image
        mobile = render_variant(
            mobile_source,
            reference_width=MOBILE_REFERENCE_WIDTH,
            scale=MOBILE_SCALE,
            display_height=self.display_height_mobile,
            fit=self.fit_mode,
            focus=self.focus,
            background=desktop['background'],
        )

        base = self.image.name
        self.desktop_webp.save(variant_filename(base, f'{self.pk}-desktop', 'webp'), desktop['webp'], save=False)
        self.desktop_jpeg.save(variant_filename(base, f'{self.pk}-desktop', 'jpg'), desktop['jpeg'], save=False)
        self.mobile_webp.save(variant_filename(base, f'{self.pk}-mobile', 'webp'), mobile['webp'], save=False)
        self.mobile_jpeg.save(variant_filename(base, f'{self.pk}-mobile', 'jpg'), mobile['jpeg'], save=False)

        self.desktop_width, self.desktop_height = desktop['width'], desktop['height']
        self.mobile_width, self.mobile_height = mobile['width'], mobile['height']
        self.background_color = desktop['background']
        self.render_signature = signature

        super().save(update_fields=[
            'desktop_webp', 'desktop_jpeg', 'desktop_width', 'desktop_height',
            'mobile_webp', 'mobile_jpeg', 'mobile_width', 'mobile_height',
            'background_color', 'render_signature',
        ])
