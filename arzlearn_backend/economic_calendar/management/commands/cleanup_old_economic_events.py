from django.core.management.base import BaseCommand
from django.utils import timezone

from economic_calendar.models import EconomicEvent


class Command(BaseCommand):
    """
    حذف رویدادهای اقتصادی هفته‌ای که تمام شده (تاریخ رویداد <= امروز).

    نحوه اجرا:
        python manage.py cleanup_old_economic_events

    پیشنهاد: این دستور را با یک زمان‌بند سیستم‌عامل (Task Scheduler در ویندوز،
    یا cron در لینوکس) هر «جمعه ساعت ۲۳:۵۹» اجرا کنید، درست قبل از شروع
    هفته‌ی جدید (شنبه). اینطوری همیشه فقط داده‌های هفته‌ی جاری در سایت
    باقی می‌ماند و نیازی به پاک‌سازی دستی نیست.
    """

    help = 'حذف رویدادهای اقتصادی هفته‌ی گذشته (برای اجرای خودکار هر جمعه ساعت ۲۳:۵۹)'

    def handle(self, *args, **options):
        today = timezone.localdate()
        deleted_count, _ = EconomicEvent.objects.filter(event_date__lte=today).delete()
        self.stdout.write(self.style.SUCCESS(f'{deleted_count} رویداد اقتصادی قدیمی حذف شد.'))
