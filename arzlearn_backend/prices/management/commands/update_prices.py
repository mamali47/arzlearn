import random
import time

from django.core.management.base import BaseCommand

from prices.services import update_all_prices


class Command(BaseCommand):
    """
    اجرای مداوم بروزرسانی قیمت‌ها هر ۱ دقیقه (پیش‌فرض، با کمی نوسان تصادفی).

    نحوه اجرا:
        python manage.py update_prices

    نکته: برای استفاده در پروداکشن پیشنهاد می‌شود این دستور بصورت یک
    process جدا (مثلاً با supervisor یا systemd) همیشه در حال اجرا باشد.
    هر بار که قیمتی بروزرسانی شود، فوراً از طریق WebSocket (Django Channels)
    به تمام کلاینت‌های متصل در آدرس ws/prices/ پخش می‌شود.
    """

    help = 'بروزرسانی مداوم قیمت لحظه‌ای بیت‌کوین، اتریوم، سولانا، دلار و طلای ۱۸ عیار'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval', type=float, default=60.0,
            help='فاصله زمانی بروزرسانی بر حسب ثانیه (پیش‌فرض: ۶۰ ثانیه)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(self.style.SUCCESS(
            f'شروع بروزرسانی قیمت‌ها هر ~{interval} ثانیه... (برای توقف Ctrl+C)'
        ))

        while True:
            try:
                if update_all_prices():
                    self.stdout.write(self.style.SUCCESS('قیمت‌ها با موفقیت بروزرسانی شدند.'))
                else:
                    self.stderr.write(self.style.WARNING(
                        'هیچ قیمتی این‌بار بروزرسانی نشد (به لاگ‌های بالا نگاه کن).'
                    ))
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(f'خطا در بروزرسانی قیمت‌ها: {exc}'))

            # کمی نوسان تصادفی (±۱۰ ثانیه) تا الگوی درخواست‌ها کمتر شبیه ربات باشد
            jitter = random.uniform(-10, 10)
            time.sleep(max(interval + jitter, 10))
