import json
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from articles.models import Article


def _frontend_dist_path():
    """
    مسیر پوشه‌ی build شده‌ی فرانت‌اند (خروجی `npm run build`، همان پوشه‌ای
    که nginx از آن فایل‌ها را سرو می‌کند).

    این مسیر را در .env یا متغیرهای محیطی سرور با نام FRONTEND_DIST_PATH
    مشخص کنید، مثلاً:
        FRONTEND_DIST_PATH=/var/www/arzlearn_frontend/dist
    """
    path = getattr(settings, 'FRONTEND_DIST_PATH', None) or os.environ.get('FRONTEND_DIST_PATH')
    if not path:
        raise RuntimeError(
            'متغیر FRONTEND_DIST_PATH تنظیم نشده. باید مسیر پوشه‌ی build شده‌ی '
            'فرانت‌اند (خروجی npm run build) را در .env بگذارید، مثلاً:\n'
            'FRONTEND_DIST_PATH=/var/www/arzlearn_frontend/dist'
        )
    return path


def _extract_asset_tags(index_html_path):
    """
    از فایل index.html فعلی فرانت‌اند (که Vite ساخته و اسم فایل‌هایش هر بار
    عوض می‌شود، مثل index-BvTlboFd.js)، تگ‌های <script type="module"> و
    <link rel="stylesheet"> را استخراج می‌کند تا در صفحات از پیش‌رندرشده
    هم همان‌ها استفاده شود. این‌طوری هر بار که فرانت‌اند دوباره build شود،
    این اسکریپت خودکار با فایل‌های جدید هماهنگ می‌ماند.
    """
    with open(index_html_path, encoding='utf-8') as f:
        html = f.read()

    scripts = re.findall(r'<script[^>]+type="module"[^>]*></script>', html)
    styles = re.findall(r'<link[^>]+rel="stylesheet"[^>]*/?>', html)
    favicon = re.findall(r'<link[^>]+rel="icon"[^>]*/?>', html)

    if not scripts:
        raise RuntimeError(
            f'هیچ اسکریپت React‌ای در {index_html_path} پیدا نشد. مطمئن شو قبل '
            'از اجرای این دستور، یک بار npm run build را در پوشه‌ی فرانت‌اند '
            'اجرا کرده باشی.'
        )

    return scripts, styles, favicon


def _build_article_json_ld(article, site_url):
    """معادل پایتونی همان تابع buildArticleSchema که در فرانت‌اند (src/utils/seo.ts) هست."""
    data = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        'headline': article.title,
        'description': article.summary,
        'datePublished': article.published_at.isoformat(),
        'dateModified': article.updated_at.isoformat(),
        'author': {
            '@type': 'Organization',
            'name': (article.author.get_public_name() if article.author else None) or 'ارزلرن',
        },
        'publisher': {
            '@type': 'Organization',
            'name': 'ارزلرن',
            'logo': {'@type': 'ImageObject', 'url': f'{site_url}/logo.png'},
        },
        'mainEntityOfPage': {
            '@type': 'WebPage',
            '@id': f'{site_url}/article/{article.slug}',
        },
    }
    if article.image:
        data['image'] = [f'{site_url}{article.image.url}']
    return json.dumps(data, ensure_ascii=False)


def _build_faq_json_ld(article):
    faqs = list(article.faqs.all())
    if not faqs:
        return None
    data = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': faq.question,
                'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(faq.answer)},
            }
            for faq in faqs
        ],
    }
    return json.dumps(data, ensure_ascii=False)


class Command(BaseCommand):
    help = 'برای هر مقاله‌ی منتشرشده، یک فایل HTML سئو-فرندلی از پیش‌رندرشده می‌سازد.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            help='اگر فقط می‌خواهی صفحه‌ی یک مقاله‌ی خاص دوباره ساخته شود (اختیاری).',
        )

    def handle(self, *args, **options):
        dist_path = _frontend_dist_path()
        index_html_path = os.path.join(dist_path, 'index.html')

        if not os.path.exists(index_html_path):
            raise RuntimeError(
                f'فایل {index_html_path} پیدا نشد. اول باید فرانت‌اند build شده باشد '
                '(npm run build) و FRONTEND_DIST_PATH درست تنظیم شده باشد.'
            )

        scripts, styles, favicon = _extract_asset_tags(index_html_path)
        site_url = getattr(settings, 'SITE_URL', 'https://arzlearn.ir').rstrip('/')

        articles = Article.objects.filter(status='published')
        slug_filter = options.get('slug')
        if slug_filter:
            articles = articles.filter(slug=slug_filter)

        count = 0
        for article in articles:
            html = render_to_string('articles/prerender_article.html', {
                'article': article,
                'scripts': scripts,
                'styles': styles,
                'favicon': favicon,
                'site_url': site_url,
                'canonical_url': f'{site_url}/article/{article.slug}',
                'json_ld': _build_article_json_ld(article, site_url),
                'faq_json_ld': _build_faq_json_ld(article),
            })

            out_dir = os.path.join(dist_path, 'article', article.slug)
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.join(out_dir, 'index.html')
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(html)
            count += 1

        self.stdout.write(self.style.SUCCESS(f'{count} صفحه‌ی مقاله با موفقیت ساخته شد.'))
