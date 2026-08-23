from django.conf import settings
from django.db import models


class Wallet(models.Model):
    """
    Each user gets exactly one wallet. `balance` is spendable/withdrawable
    (rental-fee payouts land here). `escrow_hold` is informational — the
    real escrow ledger of truth is Payment.deposit_status, this field just
    lets a lender see "X currently held on your behalf" without a join.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
      constraints = [
    models.CheckConstraint(check=models.Q(balance__gte=0), name="wallet_balance_non_negative"),
]

    def __str__(self):
        return f"Wallet({self.user_id}) = {self.balance}"


class WalletTransaction(models.Model):
    """Append-only ledger entry backing every balance change. Never mutated, only inserted."""

    class Kind(models.TextChoices):
        RENTAL_PAYOUT = "RENTAL_PAYOUT", "Rental fee payout to lender"
        DEPOSIT_REFUND = "DEPOSIT_REFUND", "Security deposit refund to renter"
        DEPOSIT_FORFEIT = "DEPOSIT_FORFEIT", "Security deposit forfeited to lender"
        ADJUSTMENT = "ADJUSTMENT", "Manual adjustment"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, null=True, blank=True, related_name="ledger_entries")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # always positive; sign implied by kind
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.kind} {self.amount} -> wallet {self.wallet_id}"


class Payment(models.Model):
    """
    Single financial record per booking. Split payment logic:
      rental_fee      -> credited immediately to lender's Wallet on success
      security_deposit -> held here (deposit_status=HELD), NOT in anyone's
                           wallet, until COMPLETED (refund) or DISPUTED
                           resolution (forfeit).
    """

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Fully Refunded"

    class DepositStatus(models.TextChoices):
        HELD = "HELD", "Held in Escrow"
        REFUNDED = "REFUNDED", "Refunded to Renter"
        FORFEITED = "FORFEITED", "Forfeited to Lender"
        DISPUTED = "DISPUTED", "Under Dispute"

    booking = models.OneToOneField("bookings.Booking", on_delete=models.PROTECT, related_name="payment")
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_made")
    lender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_received")

    rental_fee = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)

    # Idempotency: client generates this once (e.g. UUID) and resends it on
    # retry; we look it up before creating a new Payment/charging the gateway.
    idempotency_key = models.CharField(max_length=100, unique=True)

    gateway = models.CharField(max_length=50, default="razorpay")
    gateway_order_id = models.CharField(max_length=120, blank=True, null=True, unique=True)
    gateway_payment_id = models.CharField(max_length=120, blank=True, null=True, unique=True)

    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    deposit_status = models.CharField(max_length=20, choices=DepositStatus.choices, default=DepositStatus.HELD)

    payout_released_at = models.DateTimeField(null=True, blank=True)
    deposit_resolved_at = models.DateTimeField(null=True, blank=True)

    failure_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["deposit_status"]),
        ]

    def __str__(self):
        return f"Payment(booking={self.booking_id}) {self.status}/{self.deposit_status}"

    def to_summary_dict(self) -> dict:
        return {
            "booking_id": self.booking.public_id.hex,
            "rental_fee": str(self.rental_fee),
            "security_deposit": str(self.security_deposit),
            "total_paid": str(self.total_paid),
            "status": self.status,
            "deposit_status": self.deposit_status,
            "gateway_payment_id": self.gateway_payment_id,
            "updated_at": self.updated_at.isoformat(),
        }
