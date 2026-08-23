from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/bookings/(?P<booking_id>[0-9a-f-]+)/$", consumers.BookingConsumer.as_asgi()),
    re_path(r"ws/notifications/$", consumers.UserNotificationConsumer.as_asgi()),
]
