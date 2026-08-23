import logging

try:
    from celery import shared_task
except ImportError:  # allow this module to import even without Celery installed
    def shared_task(*args, **kwargs):
        def wrapper(fn):
            return fn
        return wrapper

logger = logging.getLogger(__name__)


@shared_task(name="bookings.expire_stale_approved_bookings")
def expire_stale_approved_bookings():
    """
    Celery beat schedule (settings.py):

        CELERY_BEAT_SCHEDULE = {
            "expire-stale-bookings": {
                "task": "bookings.expire_stale_approved_bookings",
                "schedule": 300.0,  # every 5 minutes
            },
        }

    Flips any APPROVED booking whose 48h payment window has lapsed to
    EXPIRED. The item was never marked unavailable at APPROVED time
    (that only happens on ACTIVE), so nothing needs to be relisted here —
    it's already bookable by others once EXPIRED.
    """
    from .utils import sweep_expired_bookings

    count = sweep_expired_bookings()
    if count:
        logger.info("Auto-expired %d approved bookings past the 48h payment window.", count)
    return count


@shared_task(name="bookings.dispatch_booking_webhook", bind=True, max_retries=5, default_retry_delay=30)
def dispatch_booking_webhook(self, payload: dict):
    """
    Sends the same payload pushed over WebSocket to any partner-registered
    webhook URL, with basic retry/backoff. Swap the URL source for your
    actual `WebhookSubscription` model.
    """
    import requests
    from django.conf import settings

    webhook_urls = getattr(settings, "BOOKING_WEBHOOK_URLS", [])
    for url in webhook_urls:
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("Webhook delivery to %s failed: %s", url, exc)
            raise self.retry(exc=exc)
