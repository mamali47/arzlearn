from django.core.management.base import BaseCommand

from economic_calendar.services import update_week_economic_events


class Command(BaseCommand):
    """
    بروزرسانی تقویم اقتصادی هفته‌ی جاری.

    نحوه اجرا (پیشنهاد: هر شنبه صبح، یک بار در هفته):
        python manage.py update_economic_calendar

    برای اجرای خودکار هفتگی، این دستور را با یک ابزار زمان‌بند (مثل cron در
    لینوکس، یا Task Scheduler در ویندوز) هر شنبه ساعت ۰۰:۰۱ اجرا کنید.
    """

    help = 'دریافت و بروزرسانی رویدادهای تقویم اقتصادی هفته‌ی جاری از API خارجی'

    def handle(self, *args, **options):
        count = update_week_economic_events()
        if count:
            self.stdout.write(self.style.SUCCESS(f'{count} رویداد اقتصادی با موفقیت بروزرسانی شد.'))
        else:
            self.stdout.write(self.style.WARNING(
                'هیچ رویدادی دریافت نشد. لاگ‌ها را برای جزئیات خطا بررسی کنید '
                '(احتمالاً ECONOMIC_CALENDAR_API_KEY تنظیم نشده یا API در دسترس نیست).'
            ))
