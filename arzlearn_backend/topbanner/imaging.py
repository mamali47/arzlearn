"""
پردازش خودکار تصویر بنر بالای سایت.

هدف: هر تصویری که در ادمین جنگو آپلود می‌شود — با هر ابعاد و هر فرمتی —
خودکار به دو نسخه‌ی استاندارد تبدیل شود:

    • نسخه‌ی دسکتاپ : نسبت تصویرِ نوار دسکتاپ
    • نسخه‌ی موبایل : نسبت تصویرِ نوار موبایل (بلندتر و مربع‌تر، تا متن بنر
                      روی گوشی ریز و ناخوانا نشود)

هر نسخه در دو فرمت ذخیره می‌شود: WebP (سبک، برای همه‌ی مرورگرهای مدرن) و
JPEG به‌عنوان fallback. ابعاد دقیق هر نسخه در دیتابیس ذخیره می‌شود تا
فرانت‌اند بتواند width/height بگذارد و صفحه هنگام لود شدن بنر «نپرد»
(Cumulative Layout Shift = 0، که یکی از فاکتورهای Core Web Vitals گوگل است).
"""

import io
import os

from django.core.files.base import ContentFile
from PIL import Image, ImageColor, ImageOps

# عرض مرجع ظرفِ بنر (همان --max-width سایت) و عرض مرجع گوشی.
DESKTOP_REFERENCE_WIDTH = 1240
MOBILE_REFERENCE_WIDTH = 430

# ضریب رتینا: تصویر با این ضریب بزرگ‌تر رندر می‌شود تا روی نمایشگرهای
# چگالی‌بالا هم شارپ بماند.
DESKTOP_SCALE = 2
MOBILE_SCALE = 3

WEBP_QUALITY = 82
JPEG_QUALITY = 86


def _load(image_field) -> Image.Image:
    """باز کردن فایل آپلودشده، اصلاح چرخش EXIF و تبدیل به RGB."""
    image_field.open()
    image_field.seek(0)
    img = Image.open(image_field)
    img = ImageOps.exif_transpose(img)

    if img.mode in ('RGBA', 'LA', 'P'):
        # روی پس‌زمینه‌ی سفید فلت می‌کنیم تا JPEG هم درست دربیاید.
        background = Image.new('RGB', img.size, (255, 255, 255))
        converted = img.convert('RGBA')
        background.paste(converted, mask=converted.split()[-1])
        img = background
    else:
        img = img.convert('RGB')

    return img


def dominant_edge_color(img: Image.Image) -> str:
    """
    رنگ غالب لبه‌های تصویر را برمی‌گرداند (مثل #f5c518).

    از این رنگ برای دو چیز استفاده می‌شود: پس‌زمینه‌ی نوار بنر وقتی حالت
    «contain» انتخاب شده، و رنگ placeholder قبل از لود شدن تصویر.
    """
    small = img.resize((32, 32), Image.Resampling.LANCZOS)
    pixels = small.load()
    samples = []
    for x in range(32):
        samples.append(pixels[x, 0])
        samples.append(pixels[x, 31])
    for y in range(32):
        samples.append(pixels[0, y])
        samples.append(pixels[31, y])

    r = sum(p[0] for p in samples) // len(samples)
    g = sum(p[1] for p in samples) // len(samples)
    b = sum(p[2] for p in samples) // len(samples)
    return f'#{r:02x}{g:02x}{b:02x}'


def _fit_cover(img: Image.Image, size, focus: str) -> Image.Image:
    """
    تصویر را طوری برش می‌زند که دقیقاً کل کادر را پر کند (هیچ حاشیه‌ای
    نمی‌ماند ولی ممکن است کمی از لبه‌ها بریده شود).
    """
    centering = {
        'right': (1.0, 0.5),
        'left': (0.0, 0.5),
        'center': (0.5, 0.5),
    }.get(focus, (0.5, 0.5))
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=centering)


def _fit_contain(img: Image.Image, size, background: str) -> Image.Image:
    """
    کل تصویر را بدون هیچ برشی داخل کادر جا می‌دهد و فضای خالی را با رنگ
    پس‌زمینه پر می‌کند. برای بنرهایی که متنشان تا لبه آمده مناسب است.
    """
    target_w, target_h = size
    canvas = Image.new('RGB', size, ImageColor.getrgb(background))
    copy = img.copy()
    copy.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    offset = ((target_w - copy.width) // 2, (target_h - copy.height) // 2)
    canvas.paste(copy, offset)
    return canvas


def _encode(img: Image.Image, fmt: str) -> ContentFile:
    buffer = io.BytesIO()
    if fmt == 'webp':
        img.save(buffer, 'WEBP', quality=WEBP_QUALITY, method=6)
    else:
        img.save(buffer, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
    return ContentFile(buffer.getvalue())


def render_variant(source_field, *, reference_width, scale, display_height, fit, focus,
                   background=None):
    """
    یک نسخه (دسکتاپ یا موبایل) از بنر می‌سازد.

    خروجی: دیکشنری شامل فایل WebP، فایل JPEG، عرض، ارتفاع و رنگ پس‌زمینه.
    """
    img = _load(source_field)
    bg = background or dominant_edge_color(img)

    target_width = reference_width * scale
    target_height = max(1, round(display_height * scale))
    size = (target_width, target_height)

    rendered = (
        _fit_contain(img, size, bg) if fit == 'contain' else _fit_cover(img, size, focus)
    )

    return {
        'webp': _encode(rendered, 'webp'),
        'jpeg': _encode(rendered, 'jpeg'),
        'width': target_width,
        'height': target_height,
        'background': bg,
    }


def variant_filename(source_name: str, suffix: str, extension: str) -> str:
    base = os.path.splitext(os.path.basename(source_name or 'banner'))[0]
    return f'{base}-{suffix}.{extension}'
