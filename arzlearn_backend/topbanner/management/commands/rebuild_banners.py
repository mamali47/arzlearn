from django.core.management.base import BaseCommand

from topbanner.models import TopBanner


class Command(BaseCommand):
    help = 'نسخه‌های بهینه‌ی دسکتاپ و موبایل همه‌ی بنرها را دوباره می‌سازد.'

    def handle(self, *args, **options):
        count = 0
        for banner in TopBanner.objects.all():
            banner.render_signature = ''   # اجبار به ساخت دوباره
            banner.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} بنر دوباره ساخته شد.'))
