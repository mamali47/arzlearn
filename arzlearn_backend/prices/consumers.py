import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

PRICES_GROUP_NAME = 'prices_updates'


class PriceConsumer(AsyncWebsocketConsumer):
    """
    WebSocket endpoint: ws://<host>/ws/prices/

    - هنگام اتصال، بلافاصله آخرین قیمت‌های موجود در دیتابیس ارسال می‌شود.
    - بعد از آن، هر بار که دستور مدیریتی `update_prices` قیمت جدیدی ذخیره کند
      (از طریق prices/services.py -> broadcast_price_update)، پیام بروزرسانی
      برای تمام کلاینت‌های متصل به این گروه پخش می‌شود.
    """

    async def connect(self):
        await self.channel_layer.group_add(PRICES_GROUP_NAME, self.channel_name)
        await self.accept()

        prices = await self._get_serialized_prices()
        await self.send(text_data=json.dumps({'type': 'snapshot', 'prices': prices}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(PRICES_GROUP_NAME, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # این کانسومر یک‌طرفه است (فقط سرور -> کلاینت)؛ پیام ورودی از کلاینت
        # پردازش خاصی نیاز ندارد، اما اگر کلاینت "ping" بفرستد "pong" پاسخ می‌دهیم
        # تا اتصال زنده نگه داشته شود.
        if text_data == 'ping':
            await self.send(text_data='pong')

    # این متد handler پیام‌های گروهی با type="price.update" است
    # (Channels به‌صورت خودکار نقطه را به آندرلاین تبدیل می‌کند).
    async def price_update(self, event):
        await self.send(text_data=json.dumps({'type': 'update', 'prices': event['prices']}))

    @database_sync_to_async
    def _get_serialized_prices(self):
        from .models import Price
        from .serializers import PriceSerializer

        return PriceSerializer(Price.objects.all(), many=True).data
