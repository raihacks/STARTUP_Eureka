"""
Optional — only used if Django Channels is installed/configured.
Mobile clients open one socket per booking detail screen, and one
per-user socket for dashboard/list-level badge updates.

wire up in bookings/routing.py + project asgi.py (see README).
"""
try:
    from channels.generic.websocket import AsyncJsonWebsocketConsumer
except ImportError:
    AsyncJsonWebsocketConsumer = object  # import-safe stub if channels absent


class BookingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.booking_public_id = self.scope["url_route"]["kwargs"]["booking_id"]
        self.group_name = f"booking_{self.booking_public_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def booking_event(self, event):
        """Handler name must match the `type` key sent via group_send (dots -> underscores)."""
        await self.send_json(event["payload"])


class UserNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close()
            return
        self.group_name = f"user_{user.id}_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def booking_event(self, event):
        await self.send_json(event["payload"])
