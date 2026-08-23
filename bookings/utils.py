from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Booking, BookingEvent


class OverlapError(Exception):
    """Raised when requested dates collide with an existing blocking booking."""


def quote_price(product, start_date, end_date) -> dict:
    """Pure pricing calc — kept out of views so API and web share one source of truth."""
    if end_date < start_date:
        raise ValueError("end_date cannot be before start_date")

    duration_days = (end_date - start_date).days + 1
    rental_price = (Decimal(duration_days) * product.rental_price).quantize(Decimal("0.01"))
    deposit_amount = product.security_deposit
    total_price = rental_price + deposit_amount
    return {
        "duration_days": duration_days,
        "rental_price": rental_price,
        "deposit_amount": deposit_amount,
        "total_price": total_price,
    }


def has_overlap(product, start_date, end_date, *, exclude_booking_id=None) -> bool:
    """
    True if [start_date, end_date] overlaps any booking currently holding
    the calendar for this product (PENDING/APPROVED/PAID/ACTIVE).
    Classic interval overlap test: (StartA <= EndB) and (EndA >= StartB).
    """
    qs = Booking.objects.filter(
        product=product,
        status__in=Booking.BLOCKING_STATUSES,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
    if exclude_booking_id:
        qs = qs.exclude(pk=exclude_booking_id)
    return qs.exists()


@transaction.atomic
def create_booking_request(*, product, renter, start_date, end_date):
    """
    Row-locks the product to make the overlap-check + insert atomic,
    so two simultaneous requests for the same dates can't both succeed.
    """
    from products.models import Product  # local import avoids app-loading cycles

    locked_product = Product.objects.select_for_update().get(pk=product.pk)

    if renter_id_equals_owner := (renter.id == locked_product.owner_id):
        raise ValueError("You cannot book your own listing.")

    if has_overlap(locked_product, start_date, end_date):
        raise OverlapError("These dates are no longer available for this item.")

    quote = quote_price(locked_product, start_date, end_date)

    booking = Booking.objects.create(
        product=locked_product,
        renter=renter,
        lender=locked_product.owner,
        start_date=start_date,
        end_date=end_date,
        rental_price=quote["rental_price"],
        deposit_amount=quote["deposit_amount"],
        total_price=quote["total_price"],
        status=Booking.Status.PENDING,
    )
    BookingEvent.objects.create(
        booking=booking, from_status="", to_status=Booking.Status.PENDING, actor=renter
    )
    return booking


@transaction.atomic
def transition_booking(*, booking_id, new_status, actor, metadata=None, lock=True):
    """
    Generic guarded transition helper shared by web views, API views, and
    the auto-expiration sweep. Locks the row to avoid double-processing
    (e.g. a customer paying at the exact moment auto-expiry fires).
    """
    qs = Booking.objects.select_for_update() if lock else Booking.objects
    booking = qs.get(pk=booking_id)
    from_status = booking.status
    booking.transition_to(new_status)
    BookingEvent.objects.create(
        booking=booking,
        from_status=from_status,
        to_status=new_status,
        actor=actor,
        metadata=metadata or {},
    )
    return booking


def check_and_expire_booking(booking: Booking):
    """
    Lazy, on-read expiry check — called from customer/lender views so the
    UI is correct even between scheduled sweeps. Safe to call frequently;
    it's a no-op unless the booking is actually past its payment window.
    """
    if booking.is_payment_window_expired:
        with transaction.atomic():
            transition_booking(
                booking_id=booking.pk,
                new_status=Booking.Status.EXPIRED,
                actor=None,
                metadata={"reason": "payment_window_lazy_check"},
            )
        booking.refresh_from_db()
    return booking


@transaction.atomic
def sweep_expired_bookings() -> int:
    """
    Batch version for Celery beat / cron. Returns count of bookings expired.
    Relisting the item is implicit: Product.available was never flipped to
    False for an APPROVED-but-unpaid booking, so nothing else to undo here.
    """
    expired_count = 0
    stale = list(
        Booking.objects.select_for_update()
        .filter(status=Booking.Status.APPROVED, approval_expires_at__lte=timezone.now())
    )
    for booking in stale:
        transition_booking(
            booking_id=booking.pk,
            new_status=Booking.Status.EXPIRED,
            actor=None,
            metadata={"reason": "payment_window_sweep"},
        )
        expired_count += 1
    return expired_count
