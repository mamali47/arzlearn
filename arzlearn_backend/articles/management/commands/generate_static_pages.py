"""
ساخت نسخه‌ی ایستا و سئو-فرندلیِ صفحات سایت.

سایت ارزلرن یک SPA ری‌اکتی است؛ یعنی HTML خالی به مرورگر می‌رسد و محتوا با
جاوااسکریپت ساخته می‌شود. گوگل‌بات معمولاً جاوااسکریپت را اجرا می‌کند، اما:

  • این کار در صف دوم رندر انجام می‌شود و گاهی روزها طول می‌کشد؛
  • خزنده‌ی بینگ، ربات تلگرام، توییتر، واتساپ و ابزارهای سئو اصلاً JS اجرا نمی‌کنند؛
  • صفحه‌ی خالی یعنی LCP بد و امتیاز پایین Core Web Vitals.

این دستور برای هر مسیر مهم سایت یک فایل HTML می‌سازد که از همان اول محتوا،
تایتل، متا، canonical و JSON-LD درست را دارد و بعد ری‌اکت روی آن سوار می‌شود.

    python manage.py generate_static_pages              # همه‌ی صفحات
    python manage.py generate_static_pages --only=home  # فقط صفحه اصلی
    python manage.py generate_static_pages --slug=...   # فقط یک مقاله

بعد از هر بار `npm run build` این دستور را دوباره اجرا کن.
"""

import os
import re
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from arzlearn.seo import (
    absolute_url,
    breadcrumb_schema,
    item_list_schema,
    json_ld,
    meta_description,
    organization_schema,
    site_url,
    website_schema,
)
from articles.models import Article, Category

# نشانه‌ای که در خروجی این دستور گذاشته می‌شود تا بتوانیم فایل ساخته‌شده‌ی
# خودمان را از فایل اصلیِ Vite تشخیص دهیم.
PRERENDER_MARKER = 'arzlearn:prerendered'
PRISTINE_INDEX = '.vite-index.html'

GA_ID = os.environ.get('GA_MEASUREMENT_ID', 'G-K5677NHH50')

PRICE_ROUTES = [
    ('bitcoin', 'BTC', 'بیت‌کوین'),
    ('ethereum', 'ETH', 'اتریوم'),
    ('solana', 'SOL', 'سولانا'),
    ('bnb', 'BNB', 'بایننس کوین'),
    ('hype', 'HYPE', 'هایپرلیکوئید'),
    ('xaut', 'XAUT', 'طلا (تتر گلد)'),
    ('dollar', 'USD', 'دلار'),
    ('gold', 'GOLD18', 'طلای ۱۸ عیار'),
]

# صفحاتی که محتوای کاربردیِ قابل ایندکس ندارند. برای اینها هم HTML می‌سازیم
# (تا تایتل و متای درست داشته باشند و سوشیال پریویوشان خراب نباشد) ولی با
# noindex، چون صفحه‌ی ورود/ثبت‌نام در ایندکس گوگل فقط کیفیت دامنه را پایین می‌آورد.
NOINDEX_PAGES = [
    ('login', 'ورود به حساب کاربری', 'ورود به حساب کاربری ارزلرن.'),
    ('register', 'ثبت‌نام در ارزلرن', 'ساخت حساب کاربری رایگان در ارزلرن.'),
    ('forgot-password', 'فراموشی رمز عبور', 'بازیابی رمز عبور حساب کاربری ارزلرن.'),
    ('reset-password', 'تعیین رمز عبور جدید', 'تعیین رمز عبور جدید برای حساب کاربری ارزلرن.'),
    ('verify-email', 'تایید ایمیل', 'تایید آدرس ایمیل حساب کاربری ارزلرن.'),
    ('check-email', 'ایمیلتان را بررسی کنید', 'لینک تایید به ایمیل شما ارسال شد.'),
    ('search', 'جستجو در ارزلرن', 'جستجو در اخبار، تحلیل‌ها و آموزش‌های ارزلرن.'),
]


def _dist_path():
    path = getattr(settings, 'FRONTEND_DIST_PATH', None) or os.environ.get('FRONTEND_DIST_PATH')
    if not path:
        raise RuntimeError(
            'متغیر FRONTEND_DIST_PATH تنظیم نشده. مسیر پوشه‌ی build شده‌ی فرانت‌اند '
            'را در .env بگذار، مثلاً:\nFRONTEND_DIST_PATH=/var/www/arzlearn_frontend/dist'
        )
    return path


def _read_template_html(dist_path):
    """
    HTML اصلیِ ساخته‌شده توسط Vite را برمی‌گرداند.

    نکته‌ی مهم: خروجی این دستور خودش روی dist/index.html نوشته می‌شود (چون
    صفحه‌ی اصلی سایت همان فایل است). پس اگر دفعه‌ی بعد دوباره از همان فایل
    اسم اسکریپت‌ها را بخوانیم، داریم از خروجیِ خودمان می‌خوانیم. برای همین
    یک نسخه‌ی دست‌نخورده از خروجی Vite در `.vite-index.html` نگه می‌داریم.
    """
    index_path = os.path.join(dist_path, 'index.html')
    pristine_path = os.path.join(dist_path, PRISTINE_INDEX)

    if not os.path.exists(index_path):
        raise RuntimeError(
            f'فایل {index_path} پیدا نشد. اول باید در پوشه‌ی فرانت‌اند '
            '`npm run build` اجرا شده باشد و FRONTEND_DIST_PATH درست باشد.'
        )

    with open(index_path, encoding='utf-8') as f:
        html = f.read()

    if PRERENDER_MARKER not in html:
        # این خروجیِ تازه‌ی Vite است؛ ازش یک نسخه‌ی پشتیبان می‌گیریم.
        shutil.copyfile(index_path, pristine_path)
        return html

    if os.path.exists(pristine_path):
        with open(pristine_path, encoding='utf-8') as f:
            return f.read()

    raise RuntimeError(
        'index.html فعلی خروجیِ همین دستور است و نسخه‌ی اصلی Vite '
        f'({PRISTINE_INDEX}) هم موجود نیست. یک بار `npm run build` بزن و '
        'دوباره این دستور را اجرا کن.'
    )


def _extract_assets(html):
    """
    تگ‌های اسکریپت/استایل/فاوآیکون خروجی Vite (که هشِ اسمشان هر build عوض
    می‌شود) را از HTML اصلی بیرون می‌کشد تا صفحات ساخته‌شده همیشه با آخرین
    build هماهنگ بمانند.
    """
    scripts = re.findall(r'<script[^>]+type="module"[^>]*></script>', html)
    styles = re.findall(r'<link[^>]+rel="stylesheet"[^>]*/?>', html)
    favicon = re.findall(r'<link[^>]+rel="icon"[^>]*/?>', html)
    modulepreloads = re.findall(r'<link[^>]+rel="modulepreload"[^>]*/?>', html)

    if not scripts:
        raise RuntimeError(
            'هیچ اسکریپت ری‌اکتی در index.html پیدا نشد. مطمئن شو قبل از اجرای '
            'این دستور یک بار `npm run build` زده‌ای.'
        )

    # preload فایل CSS باعث می‌شود مرورگر زودتر شروع به دانلودش کند (LCP بهتر).
    preloads = []
    for tag in styles:
        href = re.search(r'href="([^"]+)"', tag)
        if href:
            preloads.append(f'<link rel="preload" as="style" href="{href.group(1)}" />')
    preloads.extend(modulepreloads)

    return {'scripts': scripts, 'styles': styles, 'favicon': favicon, 'preloads': preloads}


def _write(dist_path, route, html):
    """نوشتن HTML در مسیر درست؛ '/' یعنی خود dist/index.html."""
    if route in ('', '/'):
        out_file = os.path.join(dist_path, 'index.html')
    else:
        out_dir = os.path.join(dist_path, *route.strip('/').split('/'))
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, 'index.html')

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)
    return out_file


class Command(BaseCommand):
    help = 'ساخت نسخه‌ی ایستای سئو-فرندلی صفحه اصلی، دسته‌بندی‌ها، قیمت‌ها، مقالات و صفحات ثابت.'

    def add_arguments(self, parser):
        parser.add_argument('--slug', help='فقط یک مقاله‌ی مشخص را دوباره بساز.')
        parser.add_argument(
            '--only',
            help='فقط یک بخش را بساز: home | articles | categories | prices | static',
        )

    # ------------------------------------------------------------------ اجرا
    def handle(self, *args, **options):
        dist_path = _dist_path()
        self.assets = _extract_assets(_read_template_html(dist_path))
        self.dist_path = dist_path
        self.site_url = site_url()
        self.default_og = f'{self.site_url}/logo.png'
        self.categories = list(
            Category.objects.filter(parent__isnull=True, is_active=True).order_by('order', 'name')
        )

        only = options.get('only')
        slug = options.get('slug')
        made = 0

        if slug:
            made += self.build_articles(slug=slug)
            self.stdout.write(self.style.SUCCESS(f'{made} صفحه ساخته شد.'))
            return

        if only in (None, 'home'):
            made += self.build_home()
        if only in (None, 'articles'):
            made += self.build_articles()
        if only in (None, 'categories'):
            made += self.build_categories()
        if only in (None, 'prices'):
            made += self.build_prices()
        if only in (None, 'static'):
            made += self.build_static_pages()

        self.stdout.write(self.style.SUCCESS(f'{made} صفحه‌ی ایستا با موفقیت ساخته شد.'))

    # -------------------------------------------------------------- کمکی‌ها
    def render(self, template, route, context):
        base = {
            'assets': self.assets,
            'site_url': self.site_url,
            'canonical_url': absolute_url(route),
            'og_image': self.default_og,
            'ga_id': GA_ID,
            'categories': self.categories,
        }
        base.update(context)
        html = render_to_string(template, base)
        _write(self.dist_path, route, html)

    # ------------------------------------------------------------ صفحه اصلی
    def build_home(self):
        from exchanges.models import Exchange
        from prices.models import Price

        news = list(self._category_articles('اخبار')[:9])
        analysis = list(self._category_articles('تحلیل')[:6])

        symbol_to_slug = {symbol: slug for slug, symbol, _ in PRICE_ROUTES}
        prices = []
        for price in Price.objects.all():
            if price.symbol in symbol_to_slug:
                price.slug = symbol_to_slug[price.symbol]
                prices.append(price)

        description = (
            'ارزلرن مرجع اخبار، تحلیل و قیمت لحظه‌ای بیت‌کوین، اتریوم، سولانا، '
            'دلار و طلا؛ همراه با معرفی صرافی‌ها، تقویم اقتصادی و آموزش‌های کاربردی بازار.'
        )

        blocks = [
            json_ld(organization_schema()),
            json_ld(website_schema()),
        ]
        if news:
            blocks.append(json_ld(item_list_schema(news, 'آخرین اخبار ارزهای دیجیتال')))

        self.render('articles/prerender_home.html', '/', {
            'page_title': 'ارزلرن | اخبار، تحلیل و قیمت لحظه‌ای ارزهای دیجیتال، دلار و طلا',
            'page_description': description,
            'json_ld_blocks': blocks,
            'news': news,
            'analysis': analysis,
            'prices': prices,
            'exchanges': list(Exchange.objects.all()[:8]),
        })
        return 1

    def _category_articles(self, name):
        category = Category.objects.filter(name__iexact=name, is_active=True).first()
        if not category:
            return Article.objects.none()
        return (
            Article.objects.filter(
                category_id__in=category.get_self_and_descendant_ids(), status='published'
            )
            .select_related('category')
            .order_by('-published_at')
        )

    # --------------------------------------------------------------- مقالات
    def build_articles(self, slug=None):
        queryset = (
            Article.objects.filter(status='published')
            .select_related('category', 'author')
            .prefetch_related('faqs', 'main_tags')
        )
        if slug:
            queryset = queryset.filter(slug=slug)

        count = 0
        for article in queryset:
            route = f'/article/{article.slug}'
            faqs = list(article.faqs.all())

            article_schema = {
                '@context': 'https://schema.org',
                '@type': 'NewsArticle',
                'headline': article.title[:110],
                'description': meta_description(article.summary),
                'datePublished': article.published_at.isoformat(),
                'dateModified': article.updated_at.isoformat(),
                'inLanguage': 'fa-IR',
                'wordCount': len(re.sub(r'<[^>]+>', ' ', article.body or '').split()),
                'articleSection': article.category.name,
                'keywords': ', '.join(tag.name for tag in article.main_tags.all()),
                'author': {
                    '@type': 'Organization',
                    'name': (article.author.get_public_name() if article.author else None) or 'ارزلرن',
                    'url': f'{self.site_url}/about',
                },
                'publisher': {'@id': f'{self.site_url}/#organization'},
                'mainEntityOfPage': {'@type': 'WebPage', '@id': absolute_url(route)},
            }
            if article.image:
                article_schema['image'] = [f'{self.site_url}{article.image.url}']

            blocks = [
                json_ld(article_schema),
                json_ld(breadcrumb_schema([
                    ('ارزلرن', '/'),
                    (article.category.name, f'/category/{article.category.slug}'),
                    (article.title, route),
                ])),
            ]
            if faqs:
                blocks.append(json_ld({
                    '@context': 'https://schema.org',
                    '@type': 'FAQPage',
                    'mainEntity': [
                        {
                            '@type': 'Question',
                            'name': faq.question,
                            'acceptedAnswer': {'@type': 'Answer', 'text': meta_description(faq.answer, 500)},
                        }
                        for faq in faqs
                    ],
                }))

            related = list(
                Article.objects.filter(category=article.category, status='published')
                .exclude(pk=article.pk)
                .order_by('-published_at')[:4]
            )

            self.render('articles/prerender_article.html', route, {
                'page_title': f'{article.title} | ارزلرن',
                'page_description': meta_description(article.summary),
                'og_image': f'{self.site_url}{article.image.url}' if article.image else self.default_og,
                'json_ld_blocks': blocks,
                'article': article,
                'faqs': faqs,
                'related': related,
            })
            count += 1
        return count

    # ---------------------------------------------------------- دسته‌بندی‌ها
    def build_categories(self):
        count = 0
        for category in Category.objects.filter(is_active=True):
            route = f'/category/{category.slug}'
            articles = list(
                Article.objects.filter(
                    category_id__in=category.get_self_and_descendant_ids(), status='published'
                ).order_by('-published_at')[:20]
            )
            description = meta_description(
                f'جدیدترین مطالب دسته‌بندی {category.name} در ارزلرن؛ '
                f'{"، ".join(a.title for a in articles[:3])}.'
            )

            crumbs = [('ارزلرن', '/')]
            if category.parent:
                crumbs.append((category.parent.name, f'/category/{category.parent.slug}'))
            crumbs.append((category.name, route))

            self.render('articles/prerender_category.html', route, {
                'page_title': f'{category.name} | ارزلرن',
                'page_description': description,
                'json_ld_blocks': [
                    json_ld(breadcrumb_schema(crumbs)),
                    json_ld(item_list_schema(articles, category.name)),
                ],
                'category': category,
                'children': list(category.children.filter(is_active=True)),
                'articles': articles,
            })
            count += 1
        return count

    # ------------------------------------------------------------- قیمت‌ها
    def build_prices(self):
        from prices.models import Price

        prices = {p.symbol: p for p in Price.objects.all()}
        count = 0
        for slug, symbol, name in PRICE_ROUTES:
            route = f'/price/{slug}'
            price = prices.get(symbol)
            title = f'قیمت {name} امروز'
            unit = 'دلار' if price and price.currency == 'USD' else 'ریال'

            faqs = [
                {
                    'question': f'قیمت {name} امروز چقدر است؟',
                    'answer': (
                        f'قیمت لحظه‌ای {name} در ارزلرن به‌صورت خودکار و هر دقیقه '
                        f'بروزرسانی می‌شود و بر حسب {unit} نمایش داده می‌شود.'
                    ),
                },
                {
                    'question': f'قیمت {name} هر چند وقت یک‌بار بروزرسانی می‌شود؟',
                    'answer': f'قیمت {name} در ارزلرن هر دقیقه به‌صورت خودکار بروزرسانی می‌شود.',
                },
            ]

            self.render('articles/prerender_price.html', route, {
                'page_title': f'{title} | ارزلرن',
                'page_description': f'قیمت لحظه‌ای {name} بر حسب {unit}؛ بروزرسانی خودکار هر دقیقه در ارزلرن.',
                'json_ld_blocks': [
                    json_ld(breadcrumb_schema([('ارزلرن', '/'), (title, route)])),
                    json_ld({
                        '@context': 'https://schema.org',
                        '@type': 'FAQPage',
                        'mainEntity': [
                            {
                                '@type': 'Question',
                                'name': faq['question'],
                                'acceptedAnswer': {'@type': 'Answer', 'text': faq['answer']},
                            }
                            for faq in faqs
                        ],
                    }),
                ],
                'asset_title': title,
                'price': price,
                'faqs': faqs,
                'other_assets': [
                    {'slug': s, 'name': n} for s, _, n in PRICE_ROUTES if s != slug
                ],
            })
            count += 1
        return count

    # -------------------------------------------------------- صفحات ثابت
    def build_static_pages(self):
        count = 0

        self.render('articles/prerender_simple.html', '/about', {
            'page_title': 'درباره ارزلرن | مجله تخصصی بازارهای مالی',
            'page_description': (
                'ارزلرن یک مجله تخصصی بازارهای مالی است: جدیدترین اخبار ارزهای دیجیتال، '
                'آموزش‌های کاربردی، تحلیل بازار، بررسی صرافی‌ها و بروکرها و قیمت لحظه‌ای ارز، دلار و طلا.'
            ),
            'heading': 'درباره ارزلرن',
            'json_ld_blocks': [
                json_ld(organization_schema()),
                json_ld(breadcrumb_schema([('ارزلرن', '/'), ('درباره ما', '/about')])),
            ],
        })
        count += 1

        self.render('articles/prerender_simple.html', '/economic-calendar', {
            'page_title': 'تقویم اقتصادی هفتگی | ارزلرن',
            'page_description': (
                'تقویم اقتصادی هفتگی؛ مهم‌ترین داده‌های اقتصادی آمریکا و جهان با تاریخ، '
                'ساعت و میزان اهمیت، برای پیش‌بینی حرکت بازار ارز دیجیتال، دلار و طلا.'
            ),
            'heading': 'تقویم اقتصادی هفتگی',
            'json_ld_blocks': [
                json_ld(breadcrumb_schema([('ارزلرن', '/'), ('تقویم اقتصادی', '/economic-calendar')])),
            ],
        })
        count += 1

        for route, heading, description in NOINDEX_PAGES:
            self.render('articles/prerender_simple.html', f'/{route}', {
                'page_title': f'{heading} | ارزلرن',
                'page_description': description,
                'heading': heading,
                'robots': 'noindex, follow',
                'json_ld_blocks': [],
            })
            count += 1

        # صفحه‌ی ۴۰۴ — nginx می‌تواند مستقیم این فایل را با کد ۴۰۴ سرو کند.
        html = render_to_string('articles/prerender_simple.html', {
            'assets': self.assets,
            'site_url': self.site_url,
            'canonical_url': f'{self.site_url}/404',
            'og_image': self.default_og,
            'ga_id': GA_ID,
            'categories': self.categories,
            'page_title': 'صفحه پیدا نشد | ارزلرن',
            'page_description': 'صفحه‌ای که دنبالش بودید پیدا نشد.',
            'heading': '۴۰۴ — صفحه پیدا نشد',
            'robots': 'noindex, follow',
            'json_ld_blocks': [],
        })
        with open(os.path.join(self.dist_path, '404.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        count += 1

        return count
