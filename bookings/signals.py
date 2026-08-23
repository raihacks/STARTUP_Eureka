"""
Real-time sync for mobile clients.

Any BookingEvent write fans out to two channels:
  1. Django Channels group `booking_{public_id}` — for clients with an open
     socket on that booking's detail screen (both customer & lender apps
     subscribe to the same group).
  2. An outbound webhook queue (Celery task) for any integrator/partner
     that registered a webhook URL, e.g. push-notification service.

This module intentionally degrades gracefully: if `channels` isn't
installed/configured, the WS push is skipped and only the webhook (or
nothing, in dev) fires. Swap `send_webhook.delay(...)` for your task queue
of choice.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BookingEvent

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    CHANNELS_AVAILABLE = True
except ImportError:  # channels not installed — WS push becomes a no-op
    CHANNELS_AVAILABLE = False


WEBSOCKET_EVENT_TYPE = "booking.state_changed"


def build_payload(event: BookingEvent) -> dict:
    booking = event.booking
    return {
        "type": WEBSOCKET_EVENT_TYPE,
        "booking_id": booking.public_id.hex,
        "product_id": booking.product_id,
        "from_status": event.from_status,
        "to_status": event.to_status,
        "actor_id": event.actor_id,
        "occurred_at": event.created_at.isoformat(),
        "booking": booking.to_summary_dict(),
    }


@receiver(post_save, sender=BookingEvent)
def push_booking_event(sender, instance: BookingEvent, created, **kwargs):
    if not created:
        return

    payload = build_payload(instance)

    if CHANNELS_AVAILABLE:
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            group_name = f"booking_{instance.booking.public_id.hex}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {"type": "booking.event", "payload": payload},
            )
            # Also push to each participant's personal notification group so
            # list/dashboard screens (not just the detail screen) refresh.
            for user_id in (instance.booking.renter_id, instance.booking.lender_id):
                async_to_sync(channel_layer.group_send)(
                    f"user_{user_id}_notifications",
                    {"type": "booking.event", "payload": payload},
                )

    # Fire-and-forget outbound webhook for external integrators.
    try:
        from .tasks import dispatch_booking_webhook
        dispatch_booking_webhook.delay(payload)
    except Exception:
        # Celery not configured in this environment (e.g. local/dev) — skip.
        pass
