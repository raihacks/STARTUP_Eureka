import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Booking(models.Model):
    """
    Owns the RENTAL LIFECYCLE STATE MACHINE only.
    It never touches money directly — the Payment & Escrow Service
    (payments app) is the single source of truth for anything financial.
    Booking only stores the *quoted* amounts so the UI/API can render
    a breakdown before payment happens.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Lender Approval"
        APPROVED = "APPROVED", "Approved — Awaiting Payment"
        REJECTED = "REJECTED", "Rejected by Lender"
        EXPIRED = "EXPIRED", "Payment Window Expired"
        PAID = "PAID", "Paid & Escrow Funded"
        ACTIVE = "ACTIVE", "Item Handed Over"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        DISPUTED = "DISPUTED", "Disputed"

    # States from which a payment window expiry check is meaningful.
    AWAITING_PAYMENT = {Status.APPROVED}

    # States that "hold" a date-range on the product (block overlapping bookings).
    BLOCKING_STATUSES = {
        Status.PENDING,
        Status.APPROVED,
        Status.PAID,
        Status.ACTIVE,
    }

    # Valid forward transitions. Enforced in save()/service methods, not just views.
    TRANSITIONS = {
        Status.PENDING: {Status.APPROVED, Status.REJECTED, Status.CANCELLED},
        Status.APPROVED: {Status.PAID, Status.EXPIRED, Status.CANCELLED},
        Status.REJECTED: set(),
        Status.EXPIRED: set(),
        Status.PAID: {Status.ACTIVE, Status.DISPUTED},
        Status.ACTIVE: {Status.COMPLETED, Status.DISPUTED},
        Status.COMPLETED: set(),
        Status.CANCELLED: set(),
        Status.DISPUTED: {Status.COMPLETED},
    }

    PAYMENT_WINDOW_HOURS = 48

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings_as_renter",
    )
    # Denormalized on purpose: the product owner can change/be reassigned in theory,
    # but a booking must always remember who it was contracted with.
    lender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings_as_lender",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    # Quoted breakdown at request time (source of truth for money is Payment).
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    approval_expires_at = models.DateTimeField(null=True, blank=True)
    handed_over_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    cancellation_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "status"]),
            models.Index(fields=["renter", "status"]),
            models.Index(fields=["lender", "status"]),
            models.Index(fields=["status", "approval_expires_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=models.F("start_date")),
                name="booking_end_date_gte_start_date",
            ),
        ]

    def __str__(self):
        return f"Booking #{self.pk} [{self.product_id}] {self.status}"

    # ---- state machine guard -------------------------------------------------

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status: str, *, save=True):
        if not self.can_transition_to(new_status):
            raise BookingStateError(
                f"Cannot move booking {self.pk} from {self.status} to {new_status}"
            )
        self.status = new_status
        if new_status == self.Status.APPROVED:
            self.approval_expires_at = timezone.now() + timedelta(hours=self.PAYMENT_WINDOW_HOURS)
        if new_status == self.Status.ACTIVE:
            self.handed_over_at = timezone.now()
        if new_status == self.Status.COMPLETED:
            self.returned_at = timezone.now()
        if save:
            self.save(update_fields=[
                "status", "approval_expires_at", "handed_over_at",
                "returned_at", "updated_at",
            ])

    @property
    def is_payment_window_expired(self) -> bool:
        return (
            self.status == self.Status.APPROVED
            and self.approval_expires_at is not None
            and timezone.now() >= self.approval_expires_at
        )

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def to_summary_dict(self) -> dict:
        """Mobile-friendly JSON contract for polling / push payload merge."""
        return {
            "id": self.public_id.hex,
            "product": {
                "id": self.product_id,
                "name": self.product.name,
            },
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "duration_days": self.duration_days,
            "rental_price": str(self.rental_price),
            "deposit_amount": str(self.deposit_amount),
            "total_price": str(self.total_price),
            "status": self.status,
            "approval_expires_at": self.approval_expires_at.isoformat() if self.approval_expires_at else None,
            "updated_at": self.updated_at.isoformat(),
        }


class BookingStateError(Exception):
    """Raised on an illegal state transition attempt."""


class BookingEvent(models.Model):
    """
    Append-only audit trail. Also doubles as the payload source for
    WebSocket / webhook fan-out (see bookings/signals.py).
    """

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="events")
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking_id}: {self.from_status} -> {self.to_status}"
