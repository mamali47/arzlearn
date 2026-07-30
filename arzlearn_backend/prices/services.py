"""
سرویس دریافت قیمت لحظه‌ای؛ از دو API واقعی (نه اسکرپ HTML):

- بیت‌کوین، اتریوم، سولانا (دلاری): از CoinGecko (api.coingecko.com) که یک
  API عمومی، مستند و بدون نیاز به کلید است و درصد تغییر ۲۴ ساعته را هم
  مستقیماً می‌دهد.
- دلار و طلای ۱۸ عیار (ریالی): از BrsApi.ir با کلید اختصاصی (BRSAPI_KEY در
  .env). ساختار پاسخ طبق مستندات رسمی brsapi.ir/free-api-gold-currency-webservice
  تایید شده است.

قبلاً از اسکرپ HTML صفحات tgju.org استفاده می‌شد که به‌خاطر محافظت Cloudflare
آن سایت بعد از مدتی همیشه بلاک می‌شد؛ APIهای واقعی این مشکل را ندارند.
"""

import logging
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'
    )
}

DISPLAY_NAMES = {
    'BTC': 'بیت کوین',
    'ETH': 'اتریوم',
    'SOL': 'سولانا',
    'USD': 'دلار',
    'GOLD18': 'طلای ۱۸ عیار',
}

CURRENCIES = {
    'BTC': 'USD',
    'ETH': 'USD',
    'SOL': 'USD',
    'USD': 'IRR',
    'GOLD18': 'IRR',
}


def _to_decimal(value):
    """تبدیل امن یک مقدار (رشته یا عدد) به Decimal."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


# --------------------------------------------------------------------------
# CoinGecko - بیت‌کوین، اتریوم، سولانا (دلاری)
# --------------------------------------------------------------------------
COINGECKO_URL = 'https://api.coingecko.com/api/v3/simple/price'
COINGECKO_IDS = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana'}


def fetch_coingecko_prices():
    """
    خروجی: دیکشنری {symbol: (price: Decimal, change_percent_24h: Decimal)}
    برای هرکدام از BTC/ETH/SOL که موفق گرفته شد.
    """
    params = {
        'ids': ','.join(COINGECKO_IDS.values()),
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
    }
    results = {}
    logger.info('در حال دریافت قیمت از CoinGecko...')

    try:
        # timeout به‌صورت (connect_timeout, read_timeout) تا هیچ‌وقت بی‌نهایت
        # منتظر یک سرور کند/بی‌جواب نمانیم.
        response = requests.get(COINGECKO_URL, params=params, headers=HEADERS, timeout=(5, 10))
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.error('خطا در دریافت قیمت از CoinGecko: %s', exc)
        return results

    for symbol, coingecko_id in COINGECKO_IDS.items():
        coin_data = data.get(coingecko_id)
        if not coin_data:
            logger.warning('CoinGecko داده‌ای برای %s (%s) برنگرداند.', symbol, coingecko_id)
            continue

        price = _to_decimal(coin_data.get('usd'))
        change = _to_decimal(coin_data.get('usd_24h_change'))

        if price is None:
            continue

        results[symbol] = (price, change if change is not None else Decimal('0'))

    return results


# --------------------------------------------------------------------------
# BrsApi.ir - دلار و طلای ۱۸ عیار (ریالی)
# مستندات رسمی (تایید شده): هر آیتم شامل symbol, name, name_en, price,
# change_percent, unit ('تومان') است. قیمت را در ۱۰ ضرب می‌کنیم تا از
# تومان به ریال (واحد بقیه‌ی فیلدهای IRR پروژه) تبدیل شود.
# --------------------------------------------------------------------------
BRSAPI_URL = 'https://Api.BrsApi.ir/Market/Gold_Currency.php'


def fetch_brsapi_gold_currency():
    """
    خروجی: دیکشنری {symbol: (price_rial, change_percent)} برای USD و GOLD18،
    برای هرکدام که موفق گرفته شد (ممکن است خالی یا ناقص باشد).
    """
    results = {}

    api_key = settings.BRSAPI_KEY
    if not api_key:
        logger.warning(
            'BRSAPI_KEY تنظیم نشده؛ دریافت قیمت دلار/طلا نادیده گرفته شد. '
            'کلید اختصاصی رایگان را از brsapi.ir بگیرید و در .env قرار دهید.'
        )
        return results

    logger.info('در حال دریافت قیمت دلار/طلا از BrsApi...')

    try:
        response = requests.get(
            BRSAPI_URL, params={'key': api_key}, headers=HEADERS, timeout=(5, 10),
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.error('خطا در دریافت/تجزیه‌ی پاسخ BrsApi: %s', exc)
        return results

    # ساختار پاسخ ممکن است یک لیست تخت باشد یا یک دیکشنری با کلیدهایی مثل
    # gold/currency (هرکدام لیست) - هر دو حالت را پشتیبانی می‌کنیم.
    items = []
    if isinstance(data, dict):
        for key in ('gold', 'currency', 'gold_currency', 'items', 'data'):
            value = data.get(key)
            if isinstance(value, list):
                items.extend(value)
        if not items:
            items = [data]
    elif isinstance(data, list):
        items = data

    for item in items:
        if not isinstance(item, dict):
            continue

        symbol_text = str(item.get('symbol') or '')
        name_text = str(item.get('name') or '')
        name_en_text = str(item.get('name_en') or '').lower()

        price_toman = _to_decimal(item.get('price'))
        change = _to_decimal(item.get('change_percent'))

        if price_toman is None:
            continue

        # تبدیل تومان به ریال (واحد استاندارد پروژه برای IRR)
        price_rial = price_toman * 10

        # دلار: دقیقاً symbol == "USD" (نه USDT_IRT که تتر است و اسمش هم
        # شامل کلمه‌ی «دلار» می‌شود؛ تطبیق قبلی روی کلمه باعث اشتباه می‌شد).
        if symbol_text == 'USD':
            results['USD'] = (price_rial, change if change is not None else Decimal('0'))

        # طلای ۱۸ عیار: باید دقیقاً «۱۸ عیار» در نام فارسی یا «18k» در نام
        # انگلیسی باشد، و سکه/طلای ۲۴ عیار/انس طلا حساب نشود.
        elif (
            ('18 عیار' in name_text or '۱۸ عیار' in name_text or '18k' in name_en_text)
            and 'سکه' not in name_text
            and 'coin' not in name_en_text
        ):
            results['GOLD18'] = (price_rial, change if change is not None else Decimal('0'))

    if 'USD' not in results or 'GOLD18' not in results:
        logger.warning(
            'دلار یا طلای ۱۸ عیار در پاسخ BrsApi پیدا نشد. نمونه‌ی خام پاسخ '
            '(۱۵۰۰ کاراکتر اول) برای بررسی: %s',
            str(data)[:1500],
        )

    return results


# --------------------------------------------------------------------------
# پخش لحظه‌ای از طریق WebSocket
# --------------------------------------------------------------------------
def broadcast_price_update():
    """پخش آخرین قیمت‌ها به کلاینت‌های WebSocket. اگر Redis نبود، فقط هشدار می‌دهد."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    from .models import Price
    from .serializers import PriceSerializer

    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        serialized_prices = PriceSerializer(Price.objects.all(), many=True).data
        async_to_sync(channel_layer.group_send)(
            'prices_updates',
            {'type': 'price.update', 'prices': serialized_prices},
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            'پخش WebSocket ناموفق بود (احتمالاً Redis در دسترس نیست)، '
            'اما قیمت‌ها در دیتابیس ذخیره شدند. جزئیات خطا: %s', exc,
        )


def update_all_prices():
    """
    یک چرخه کامل بروزرسانی از هر دو منبع (CoinGecko + brsapi).
    اگر منبع خودش درصد تغییر معتبر بدهد (مثل CoinGecko) از همان استفاده
    می‌شود؛ وگرنه با مقایسه‌ی قیمت تازه با آخرین قیمت ذخیره‌شده محاسبه می‌شود.
    """
    from .models import Price

    all_prices = {}
    all_prices.update(fetch_coingecko_prices())
    all_prices.update(fetch_brsapi_gold_currency())

    updated = False

    for symbol, (price_value, api_change_percent) in all_prices.items():
        previous = Price.objects.filter(symbol=symbol).first()

        if api_change_percent:
            change_percent = api_change_percent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        elif previous and previous.price_value:
            raw_change = ((price_value - previous.price_value) / previous.price_value) * 100
            change_percent = raw_change.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            change_percent = Decimal('0')

        logger.info(
            'قیمت %s: قبلی=%s -> جدید=%s | درصد تغییر=%s',
            symbol, previous.price_value if previous else 'ندارد', price_value, change_percent,
        )

        Price.objects.update_or_create(
            symbol=symbol,
            defaults={
                'name_fa': DISPLAY_NAMES[symbol],
                'price_value': price_value,
                'currency': CURRENCIES[symbol],
                'change_percent': change_percent,
            },
        )
        updated = True

    if updated:
        broadcast_price_update()

    return updated
