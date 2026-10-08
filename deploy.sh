#!/usr/bin/env bash
# بیلد فرانت‌اند و ساخت دوباره‌ی صفحات ایستای سئو، همیشه پشت سر هم.
#
# چرا؟ `npm run build` پوشه‌ی dist را کامل خالی می‌کند و همه‌ی HTML های
# ایستای مقاله/دسته‌بندی/قیمت پاک می‌شوند. تا وقتی generate_static_pages اجرا
# نشود، همه‌ی آدرس‌ها پوسته‌ی خالیِ index.html را می‌گیرند (و گوگل صفحات را
# تکراری یا خالی می‌بیند). این اسکریپت آن فاصله را از بین می‌برد.
#
# استفاده:  ./deploy.sh   (از ریشه‌ی پروژه، با venv بک‌اند فعال و FRONTEND_DIST_PATH تنظیم‌شده)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT/arzlearn_frontend"
npm ci
npm run build

cd "$ROOT/arzlearn_backend"
python manage.py generate_static_pages
