import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arzlearn.settings')

# get_asgi_application() باید قبل از ایمپورت هر چیزی که به مدل‌های جنگو
# وابسته است (مثل routing اپ‌ها) فراخوانی شود.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

import prices.routing  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        URLRouter(prices.routing.websocket_urlpatterns)
    ),
})
