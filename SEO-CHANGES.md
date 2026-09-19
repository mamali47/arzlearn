# راهنمای تغییرات سئو، عملکرد و UI — ارزلرن

این فایل هم توضیح می‌دهد چه چیزی عوض شد و چرا، هم دقیقاً می‌گوید روی سرور
چه کار کنی. اگر عجله داری، مستقیم برو سراغ بخش **«روی سرور چه کار کنم»**.

---

## ۱. ریشه‌ی اصلی مشکل: سایت SPA است

وقتی `view-source` صفحه‌ی اصلی را باز می‌کنی، فقط `<div id="root"></div>`
می‌بینی. یعنی HTML خالی به مرورگر می‌رسد و محتوا با جاوااسکریپت ساخته
می‌شود. چرا این برای سئو بد است:

- گوگل‌بات جاوااسکریپت را اجرا می‌کند، اما در **صف دوم رندر**. گاهی
  چند روز طول می‌کشد تا محتوای یک صفحه واقعاً دیده شود. برای سایت خبری
  که خبرش بعد از دو روز بی‌ارزش است، این یعنی از دست دادن رقابت.
- بینگ، یاندکس، ربات تلگرام، توییتر و واتساپ اصلاً JS اجرا نمی‌کنند.
  الان لینک سایتت در تلگرام بدون تصویر و بدون توضیح پیش‌نمایش می‌شود.
- HTML خالی یعنی LCP بد و امتیاز پایین Core Web Vitals.

تو این را برای مقالات با `generate_static_pages` حل کرده بودی. آن دستور
حالا **کل سایت** را پوشش می‌دهد.

### چرا صفحه‌ی اصلی قبلاً قابل prerender نبود

یک تله در کد بود: دستور، اسم فایل‌های JS/CSS (که Vite هر build هش‌شان را
عوض می‌کند) را از `dist/index.html` می‌خواند. ولی خروجی صفحه‌ی اصلی هم
باید در همان `dist/index.html` نوشته شود. یعنی دفعه‌ی بعد داشت از خروجی
خودش می‌خواند و حلقه می‌شد.

**راه‌حل:** دستور حالا اولین بار که خروجی تازه‌ی Vite را می‌بیند، یک کپی
دست‌نخورده در `dist/.vite-index.html` نگه می‌دارد و همیشه از آن می‌خواند.
تشخیص هم با یک مارکر (`arzlearn:prerendered`) داخل HTML انجام می‌شود. تست
شد: اجرای پشت سر هم دستور، خروجی سالم می‌دهد.

### حالا چه صفحاتی prerender می‌شوند

| مسیر | وضعیت |
|---|---|
| `/` صفحه اصلی | ✅ با اخبار، تحلیل‌ها، قیمت‌ها و لینک دسته‌بندی‌ها |
| `/article/<slug>` | ✅ (مثل قبل، ولی با متای کامل‌تر) |
| `/category/<slug>` | ✅ جدید |
| `/price/<slug>` × ۸ | ✅ جدید، با FAQ Schema |
| `/about`, `/economic-calendar` | ✅ جدید |
| `/login`, `/register`, `/search` و بقیه | ✅ جدید، ولی با `noindex` |
| `404.html` | ✅ جدید |

دستورهای جدید:

```bash
python manage.py generate_static_pages              # همه
python manage.py generate_static_pages --only=home  # فقط صفحه اصلی
python manage.py generate_static_pages --only=articles
python manage.py generate_static_pages --slug=...   # یک مقاله
```

---

## ۲. باگ‌هایی که پیدا شد و درست شد

### الف) آدرس‌های فارسی encode نمی‌شدند

اسلاگ‌های سایت فارسی‌اند (`allow_unicode=True`). آدرس فارسیِ خام داخل
`<link rel="canonical">` و `sitemap.xml` طبق RFC 3986 معتبر نیست.
مرورگر خودش percent-encode می‌کند، پس آدرسی که گوگل کرال می‌کند با
آدرسی که تو به عنوان canonical اعلام کرده‌ای **یکی نیست** — و این یعنی
ریسک تقسیم شدن اعتبار صفحه.

حالا:

```
https://arzlearn.ir/article/%D8%A8%DB%8C%D8%AA%DA%A9%D9%88%DB%8C%D9%86-...
```

تابع `encode_path` در `arzlearn/seo.py` (بک‌اند) و `encodePath` در
`utils/seo.ts` (فرانت‌اند) این کار را می‌کنند.

### ب) یک حفره‌ی XSS در قالب prerender

```django
<script type="application/ld+json">{{ json_ld|safe }}</script>
```

اگر تایتل یا خلاصه‌ی یک مقاله رشته‌ی `</script>` داشت، هم صفحه می‌شکست هم
می‌شد کد تزریق کرد. حالا تابع `json_ld()` کاراکترهای `< > &` را به
`\u003C` و... تبدیل می‌کند (همان کاری که خود جنگو در `json_script` می‌کند).

### ج) دامنه‌ی sitemap از هدر درخواست ساخته می‌شد

اگر sitemap از پشت پروکسی یا با دامنه‌ی بک‌اند خوانده می‌شد، آدرس‌های
داخلش غلط درمی‌آمد. حالا همیشه از `settings.SITE_URL` می‌آید و
`protocol = 'https'` ثابت است.

### د) `useSEO` متاتگ‌ها را پاک نمی‌کرد

موقع رفتن به صفحه‌ی بعد، `og:image` و بقیه‌ی متاهای صفحه‌ی قبلی باقی
می‌ماندند. حالا هر تگی که این هوک می‌سازد با `data-seo-managed` علامت
می‌خورد و مدیریت می‌شود. ضمناً اضافه شد: `robots`, `twitter:card`,
`og:locale`, `og:image` مطلق، `article:published_time`.

### ه) canonical شامل query string بود

`/search?q=بیت‌کوین` و `/search?q=اتریوم` دو صفحه‌ی جدا با canonical جدا
بودند — یعنی محتوای تکراری بی‌نهایت. حالا canonical همیشه بدون query و
بدون hash است و خود صفحه‌ی جستجو `noindex` شده.

### و) صفحه‌ی اصلی `<h1>` نداشت

اولین تیتر صفحه `<h2>آخرین اخبار</h2>` بود. یک `h1` واقعی اضافه شد
(به‌صورت یک زیرعنوان کوچک و کم‌رنگ، تا چیدمان فعلی به هم نخورد). عمداً
از متن مخفی یا `font-size: 0` استفاده نشد — گوگل آن را دستکاری رتبه
حساب می‌کند.

### ز) `/login` و `/register` داخل sitemap بودند

این صفحات محتوای یکتا ندارند و بودنشان در ایندکس فقط نسبت «صفحات
بی‌کیفیت به کل» دامنه را بدتر می‌کند. از sitemap حذف و `noindex` شدند
(هم در HTML از پیش‌ساخته، هم در `useSEO`، هم در `robots.txt`).

---

## ۳. بنر بالای سایت — همان مشکلی که گفتی

بنر قبلاً فقط `width: 100%; height: auto` داشت. یعنی یک بنر ۱۹۲۰×۶۰ روی
گوشی ۳۹۰ پیکسلی تبدیل می‌شد به نواری با ارتفاع **۱۲ پیکسل**. برای همین
ریز دیده می‌شد.

### چه شد

آپلود در ادمین همان‌طور ساده ماند، ولی حالا موقع ذخیره، Pillow خودکار
دو نسخه می‌سازد:

| نسخه | ابعاد پیش‌فرض | نمایش روی صفحه |
|---|---|---|
| دسکتاپ | ۲۴۸۰×۱۸۴ (WebP + JPEG) | عرض کامل × ۹۲ پیکسل |
| موبایل | ۱۲۹۰×۳۱۲ (WebP + JPEG) | عرض کامل × ۱۰۴ پیکسل |

نکته‌ی کلیدی: **نسخه‌ی موبایل نسبت تصویر متفاوتی دارد** (حدود ۴:۱ به
جای ۱۳:۱). یعنی به جای کوچک کردن بنر عریض، از وسطش برش می‌خورد — پس متن
بنر روی گوشی حدوداً سه برابر بزرگ‌تر دیده می‌شود.

**ارتفاع نوار ثابت است** و با تغییر اندازه‌ی پنجره کوچک و بزرگ نمی‌شود
(دقیقاً چیزی که خواستی). هر دو ارتفاع در ادمین قابل تنظیم‌اند.

فیلدهای جدید در ادمین:

- **متن جایگزین (alt)** — قبلاً هاردکد `alt="تبلیغ"` بود که برای سئو و
  اسکرین‌ریدر بی‌فایده است.
- **ارتفاع نوار در دسکتاپ / موبایل** — پیش‌فرض ۹۲ و ۱۰۴.
- **نحوه جا شدن تصویر** — `cover` (برش، پیش‌فرض) یا `contain` (کل بنر
  دیده شود، دو طرف با رنگ خود بنر پر می‌شود).
- **نقطه مهم تصویر** — وسط / راست / چپ؛ وقتی برش می‌خورد این قسمت حتماً
  حفظ می‌شود.
- **پیش‌نمایش نسخه‌های ساخته‌شده** — همان‌جا در ادمین می‌بینی نتیجه چه شکلی
  شده.

ابعاد دقیق در دیتابیس ذخیره می‌شود و فرانت‌اند `width`/`height` می‌گذارد،
پس **CLS صفر** است (صفحه موقع لود شدن بنر نمی‌پرد). CLS یکی از سه فاکتور
Core Web Vitals است.

اگر خواستی بنرهای موجود را با تنظیمات جدید دوباره بسازی:

```bash
python manage.py rebuild_banners
```

---

## ۴. چیزهای جدیدی که اضافه شد

- **`/rss.xml`** — فید RSS آخرین ۳۰ مقاله. فیدخوان‌ها، Google News و
  سرویس‌های تجمیع محتوا از RSS برای پیدا کردن مطلب جدید استفاده می‌کنند؛
  معمولاً خیلی سریع‌تر از sitemap.
- **`robots.txt` پویا** از سمت جنگو (`/robots.txt`) — نسخه‌ی استاتیک در
  `public/` هم به‌روز شد، هرکدام را که nginx سرو کند فرقی نمی‌کند.
- **sitemap به‌صورت index + بخش‌های جدا** (`sitemap-articles.xml`,
  `sitemap-categories.xml`, ...). وقتی تعداد مقالات زیاد شود گوگل مجبور
  نیست یک فایل غول‌پیکر بخواند، و در Search Console می‌فهمی دقیقاً کدام
  بخش مشکل دارد. یک ساعت هم کش می‌شود.
- **`lastmod` واقعی برای دسته‌بندی‌ها** (تاریخ آخرین مقاله‌شان).
- **Schema.org کامل‌تر**: `@graph` با Organization و WebSite در
  `index.html`، `BreadcrumbList` و `ItemList` برای صفحات فهرست،
  `NewsArticle` با `wordCount`, `articleSection`, `keywords`.
- **`hreflang`, `og:locale`, `twitter:card`, `theme-color`** در همه‌ی
  صفحات.

---

## ۵. عملکرد (Core Web Vitals)

- **تصویر LCP دیگر lazy نیست.** اسلاید اول کاروسل اخبار تقریباً همیشه
  عنصر LCP صفحه‌ی اصلی است و `loading="lazy"` داشت — یکی از رایج‌ترین
  دلایل قرمز شدن LCP در PageSpeed. حالا `priority` می‌گیرد
  (`loading="eager"` + `fetchPriority="high"`).
- **همه‌ی تصاویر `width`/`height` گرفتند** → CLS کمتر.
- **`manualChunks` در Vite**: React و Router و axios در چانک‌های جدا
  (`vendor-react` حدود ۵۳KB gzip). این فایل‌ها بین دیپلوی‌ها عوض نمی‌شوند،
  پس کاربر برگشتی دوباره دانلودشان نمی‌کند.
- **جلوگیری از پرش تم**: یک اسکریپت کوچک قبل از ری‌اکت، تم ذخیره‌شده را
  روی `<html>` می‌گذارد. قبلاً کاربر تم تاریک یک لحظه صفحه‌ی روشن می‌دید.
- **`preload` برای فایل CSS** در صفحات prerender شده.

---

## ۶. UI/UX — مخصوصاً موبایل

گفتی به سلیقه‌ی خودم؛ ظاهر کلی را دست نزدم، فقط چیزهایی که روی گوشی
واقعاً آزاردهنده بودند:

- **هدر چسبان با پس‌زمینه‌ی نیمه‌شفاف و بلور** (`backdrop-filter`) با
  fallback برای مرورگرهای قدیمی.
- **منوی موبایل تبدیل به کشوی واقعی شد**: پس‌زمینه‌ی تیره، بستن با کلیک
  بیرون، بستن با Escape، **قفل شدن اسکرول صفحه‌ی پشتی** (قبلاً منو باز
  بود و صفحه زیرش اسکرول می‌خورد)، بسته شدن خودکار موقع عوض شدن مسیر،
  و اسکرول داخلی وقتی دسته‌بندی‌ها زیاد باشند.
- **آیکون همبرگری هنگام باز بودن تبدیل به ضربدر می‌شود.**
- **هدف‌های لمسی حداقل ۴۴ پیکسل** (استاندارد اپل و گوگل). دکمه‌های
  دسته‌بندی در منوی موبایل ۳۲ پیکسل بودند.
- **فونت ورودی‌ها روی موبایل ۱۶ پیکسل** — زیر ۱۶، سافاری iOS موقع تپ
  روی فیلد کل صفحه را زوم می‌کند.
- **`safe-area-inset`** برای گوشی‌های ناچ‌دار.
- **حلقه‌ی فوکوس با `:focus-visible`** — قبلاً هیچ نشانه‌ی فوکوسی نبود
  (هم مشکل دسترس‌پذیری، هم افت امتیاز Lighthouse).
- **لینک «رفتن به محتوای اصلی»** (skip link) که فقط با Tab دیده می‌شود.
- **`prefers-reduced-motion`** رعایت شد.
- **حاشیه‌ی کانتینر روی گوشی‌های باریک** از ۲۰ به ۱۴ پیکسل.
- **جلوگیری از اسکرول افقی ناخواسته** که کاروسل‌ها ایجاد می‌کردند.
- **`aria-label`, `aria-expanded`, `role="search"`** روی هدر و کاروسل.

---

## ۷. روی سرور چه کار کنم

### گام ۱ — بک‌اند

```bash
cd arzlearn_backend
source venv/bin/activate          # یا هر اسمی که ونو دارد
pip install -r requirements.txt   # Pillow از قبل هست
python manage.py migrate
```

مطمئن شو در `.env` این‌ها هستند:

```
SITE_URL=https://arzlearn.ir
FRONTEND_DIST_PATH=/var/www/arzlearn_frontend/dist
```

### گام ۲ — فرانت‌اند

در `.env` فرانت‌اند اضافه کن:

```
VITE_SITE_URL=https://arzlearn.ir
```

بعد:

```bash
cd arzlearn_frontend
npm install
npm run build
```

### گام ۳ — ساخت صفحات ایستا (بعد از هر build)

```bash
cd arzlearn_backend
python manage.py generate_static_pages
python manage.py rebuild_banners      # یک بار، برای بنرهای موجود
```

> **ترتیب مهم است:** اول `npm run build`، بعد `generate_static_pages`.

### گام ۴ — nginx

این مهم‌ترین قسمت است. بدون `try_files` درست، فایل‌های prerender شده
اصلاً سرو نمی‌شوند و همه‌ی کار بالا بی‌اثر می‌ماند.

```nginx
# ریدایرکت www به بدون www — جلوگیری از دو نسخه‌ی موازی سایت در ایندکس
server {
    listen 443 ssl http2;
    server_name www.arzlearn.ir;
    return 301 https://arzlearn.ir$request_uri;
}

server {
    listen 443 ssl http2;
    server_name arzlearn.ir;

    root /var/www/arzlearn_frontend/dist;
    index index.html;

    charset utf-8;

    gzip on;
    gzip_vary on;
    gzip_min_length 512;
    gzip_types text/plain text/css text/xml application/json
               application/javascript application/xml+rss
               image/svg+xml application/rss+xml;
    # اگر ماژول brotli داری، خیلی بهتر است:
    # brotli on;
    # brotli_types text/css application/javascript application/json image/svg+xml;

    # ---------------- API و ادمین ----------------
    location /api/       { proxy_pass http://127.0.0.1:8000; include proxy_params; }
    location /admin/     { proxy_pass http://127.0.0.1:8000; include proxy_params; }
    location /ckeditor5/ { proxy_pass http://127.0.0.1:8000; include proxy_params; }
    location /ws/        {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        include proxy_params;
    }

    # sitemap و rss از جنگو می‌آیند (داده‌شان زنده است)
    location = /sitemap.xml { proxy_pass http://127.0.0.1:8000; include proxy_params; }
    location ~ ^/sitemap-.*\.xml$ { proxy_pass http://127.0.0.1:8000; include proxy_params; }
    location = /rss.xml     { proxy_pass http://127.0.0.1:8000; include proxy_params; }
    location = /robots.txt  { proxy_pass http://127.0.0.1:8000; include proxy_params; }

    # ---------------- فایل‌های استاتیک ----------------
    # فایل‌های assets هش دارند، پس می‌شود یک سال کششان کرد
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /media/ {
        alias /var/www/arzlearn_backend/media/;
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    location /static/ {
        alias /var/www/arzlearn_backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    # ---------------- قلب ماجرا ----------------
    # اول دنبال فایل واقعی می‌گردد، بعد دنبال پوشه‌ی prerender شده
    # (مثلاً /category/اخبار/index.html)، و در آخر index.html.
    location / {
        try_files $uri $uri/index.html /index.html;

        # صفحات HTML نباید کش شوند، وگرنه کاربر نسخه‌ی قدیمی مقاله را می‌بیند
        add_header Cache-Control "public, max-age=0, must-revalidate";
    }

    error_page 404 /404.html;
    location = /404.html { internal; }

    # فایل نسخه‌ی پشتیبان Vite نباید از بیرون قابل دسترسی باشد
    location = /.vite-index.html { deny all; }
}

# HTTP -> HTTPS
server {
    listen 80;
    server_name arzlearn.ir www.arzlearn.ir;
    return 301 https://arzlearn.ir$request_uri;
}
```

> اگر مسیر `dist` یا `media` روی سرورت فرق دارد، فقط همان‌ها را عوض کن.

### گام ۵ — کرون

بعد از انتشار هر مقاله، prerender باید دوباره اجرا شود. ساده‌ترین راه
یک کرون هر ۱۵ دقیقه:

```cron
*/15 * * * * cd /var/www/arzlearn_backend && /var/www/arzlearn_backend/venv/bin/python manage.py generate_static_pages --only=articles >> /var/log/arzlearn_prerender.log 2>&1
0 * * * *   cd /var/www/arzlearn_backend && /var/www/arzlearn_backend/venv/bin/python manage.py generate_static_pages --only=home >> /var/log/arzlearn_prerender.log 2>&1
```

> راه تمیزتر: یک سیگنال `post_save` روی مدل Article که فقط همان مقاله را
> دوباره بسازد (`--slug=`). فایل `articles/signals.py` از قبل وجود دارد و
> جای خوبی برای این کار است.

### گام ۶ — Search Console

۱. مالکیت سایت را تایید کن (کد را در `index.html` بگذار، خط کامنت‌شده
   آماده است).
۲. `https://arzlearn.ir/sitemap.xml` را ثبت کن.
۳. با ابزار **URL Inspection** یک بار صفحه‌ی اصلی و یک مقاله را تست کن؛
   در تب «HTML» باید محتوای واقعی را ببینی، نه `<div id="root"></div>`.
۴. با **Rich Results Test** یک صفحه‌ی مقاله و یک صفحه‌ی قیمت را چک کن
   (باید NewsArticle، BreadcrumbList و FAQPage را تشخیص بدهد).

---

## ۸. چک سریع بعد از دیپلوی

```bash
# باید محتوای واقعی ببینی، نه div خالی
curl -s https://arzlearn.ir/ | grep -c "<h1"

# باید canonical با percent-encoding باشد
curl -s "https://arzlearn.ir/article/<اسلاگ>" | grep canonical

# باید noindex داشته باشد
curl -s https://arzlearn.ir/login | grep robots

# sitemap index
curl -s https://arzlearn.ir/sitemap.xml | head -20

# بنر: هر دو نسخه باید برگردد
curl -s https://arzlearn.ir/api/topbanner/active/ | python3 -m json.tool
```

---

## ۹. کارهای بعدی (به ترتیب اولویت)

۱. **سیگنال `post_save` برای prerender خودکار مقاله** — تا لازم نباشد
   منتظر کرون بمانی. بیشترین برد برای کمترین کار.
۲. **صفحه‌ی `/tag/<slug>`** — کلاس `TagSitemap` نوشته شده و آماده است،
   فقط مسیر و صفحه‌اش را بساز. صفحات تگ برای کلمات کلیدی دم‌بلند عالی‌اند.
۳. **صفحه‌بندی دسته‌بندی‌ها با `rel="next"`/`rel="prev"` و canonical
   درست** — الان فقط ۲۰ مقاله‌ی اول هر دسته prerender می‌شود.
۴. **بهینه‌سازی خودکار تصویر مقالات** مثل بنر (تبدیل به WebP و ریسایز
   موقع آپلود). ماژول `topbanner/imaging.py` قابل استفاده‌ی مجدد است.
   این بزرگ‌ترین برد باقی‌مانده در Core Web Vitals است.
۵. **خودمیزبانی فونت Vazirmatn** به جای Google Fonts — هم سریع‌تر، هم
   در ایران قابل اتکاتر.
۶. **صفحه‌ی نویسنده و `sameAs` در Organization schema** (لینک اینستاگرام
   و تلگرام) — برای سیگنال E-E-A-T.
