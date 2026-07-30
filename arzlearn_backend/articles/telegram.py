"""
ارسال خودکار مقالات منتشرشده به کانال تلگرام.

نیازمند دو تنظیم در .env:
  TELEGRAM_BOT_TOKEN   - توکن بات (از @BotFather در تلگرام بگیرید)
  TELEGRAM_CHANNEL_ID  - آیدی کانال (مثلاً @arzlearn_channel یا -100xxxxxxxxxx)
                         نکته: بات باید ادمین کانال باشد تا اجازه‌ی پست کردن داشته باشد.

اگر از داخل ایران اجرا می‌کنید و تلگرام فیلتر است، یک تنظیم اختیاری هم هست:
  TELEGRAM_PROXY_URL   - آدرس یک پروکسی HTTP یا SOCKS5
                         مثال: http://127.0.0.1:10809  یا  socks5h://127.0.0.1:1080
"""

import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = 'https://api.telegram.org'
CAPTION_MAX_LENGTH = 1024
REQUEST_TIMEOUT = 25


def _build_caption(article):
    caption = f'<b>{article.title}</b>\n\n{article.summary}'
    if len(caption) > CAPTION_MAX_LENGTH:
        caption = caption[: CAPTION_MAX_LENGTH - 3] + '...'
    return caption


def _build_reply_markup(article_url):
    if not article_url:
        return None
    return json.dumps({
        'inline_keyboard': [[{'text': 'ادامه مطلب 👈', 'url': article_url}]]
    })


def _get_proxies():
    proxy_url = settings.TELEGRAM_PROXY_URL
    if not proxy_url:
        return None
    return {'http': proxy_url, 'https': proxy_url}


def post_article_to_telegram(article):
    """
    مقاله را به‌صورت یک پست (عکس + عنوان + خلاصه + دکمه‌ی ادامه مطلب) در
    کانال تلگرام ارسال می‌کند. اگر تنظیمات تلگرام خالی باشند، بی‌صدا رد می‌شود
    (بدون خطا) تا در محیط توسعه مزاحم کار نشود.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    channel_id = settings.TELEGRAM_CHANNEL_ID

    if not bot_token or not channel_id:
        logger.warning(
            'TELEGRAM_BOT_TOKEN یا TELEGRAM_CHANNEL_ID تنظیم نشده (یا سرور بعد از ویرایش .env '
            'ری‌استارت نشده)؛ ارسال مقاله «%s» به تلگرام نادیده گرفته شد.', article.title,
        )
        return False

    article_url = f'{settings.FRONTEND_BASE_URL.rstrip("/")}/article/{article.slug}'
    caption = _build_caption(article)
    reply_markup = _build_reply_markup(article_url)
    proxies = _get_proxies()

    payload = {'chat_id': channel_id, 'parse_mode': 'HTML'}
    if reply_markup:
        payload['reply_markup'] = reply_markup

    try:
        if article.image and hasattr(article.image, 'path'):
            with open(article.image.path, 'rb') as photo_file:
                response = requests.post(
                    f'{TELEGRAM_API_BASE}/bot{bot_token}/sendPhoto',
                    data={**payload, 'caption': caption},
                    files={'photo': photo_file},
                    timeout=REQUEST_TIMEOUT,
                    proxies=proxies,
                )
        else:
            response = requests.post(
                f'{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage',
                data={**payload, 'text': caption},
                timeout=REQUEST_TIMEOUT,
                proxies=proxies,
            )

        response.raise_for_status()
        result = response.json()

        if not result.get('ok'):
            logger.error('ارسال مقاله «%s» به تلگرام ناموفق بود: %s', article.title, result)
            return False

        logger.info('مقاله «%s» با موفقیت در تلگرام پست شد.', article.title)
        return True

    except requests.exceptions.Timeout:
        logger.error(
            'ارسال مقاله «%s» به تلگرام timeout شد. این معمولاً یعنی تلگرام از شبکه‌ی '
            'سرور شما فیلتر/بلاک است. یا با VPN تست کنید، یا TELEGRAM_PROXY_URL را در '
            '.env تنظیم کنید (آدرس یک پروکسی HTTP/SOCKS5).', article.title,
        )
        return False
    except requests.RequestException as exc:
        logger.error('خطا در ارسال مقاله «%s» به تلگرام: %s', article.title, exc)
        return False
