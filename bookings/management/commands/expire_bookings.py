from django.core.management.base import BaseCommand

from bookings.utils import sweep_expired_bookings


class Command(BaseCommand):
    """
    Cron alternative to Celery beat, for deployments without a task queue:

        */5 * * * *  cd /app && python manage.py expire_bookings
    """
    help = "Expire APPROVED bookings whose 48-hour payment window has lapsed."

    def handle(self, *args, **options):
        count = sweep_expired_bookings()
        self.stdout.write(self.style.SUCCESS(f"Expired {count} stale booking(s)."))
