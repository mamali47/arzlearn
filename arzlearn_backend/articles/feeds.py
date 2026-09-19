"""
فید RSS مقالات.

چرا ارزش دارد: فیدخوان‌ها، Google News، تلگرام‌بات‌ها و سرویس‌های تجمیع
محتوا از RSS برای پیدا کردن مطلب جدید استفاده می‌کنند؛ یعنی یک کانال
کشف محتوا (discovery) علاوه بر سایت‌مپ، و معمولاً خیلی سریع‌تر از آن.
"""

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from arzlearn.seo import absolute_url, meta_description, site_url

from .models import Article


class ArticleFeed(Feed):
    feed_type = Rss201rev2Feed
    title = 'ارزلرن | اخبار و تحلیل بازارهای مالی'
    description = 'جدیدترین اخبار، تحلیل‌ها و آموزش‌های ارز دیجیتال، دلار و طلا در ارزلرن.'
    language = 'fa-ir'

    def link(self):
        return f'{site_url()}/'

    def items(self):
        return (
            Article.objects.filter(status='published')
            .select_related('category')
            .order_by('-published_at')[:30]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return meta_description(item.summary, 300)

    def item_link(self, item):
        return absolute_url(f'/article/{item.slug}')

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        return [item.category.name]
