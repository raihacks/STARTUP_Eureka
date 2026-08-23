from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, BookingStateError
from bookings.utils import transition_booking

from .gateway import GatewayClient, GatewayError
from .models import Payment, Wallet, WalletTransaction


class EscrowError(Exception):
    """Raised for any invalid escrow/payment operation."""


class EscrowService:
    """
    The single choke point for anything financial. Booking Service never
    mutates money; it only calls into here (or gets called from here) via
    the state-transition helper, and every method that changes a balance
    is wrapped in @transaction.atomic with row locks to prevent double
    payouts / double refunds under concurrent requests.
    """

    # ---- 1. Customer pays -----------------------------------------------

    @staticmethod
    @transaction.atomic
    def process_payment(*, booking_id, payer, idempotency_key, gateway_payment_id, gateway_signature, raw_payload):
        """
        Verifies the gateway payment, then atomically:
          1. Creates/loads the Payment record (idempotent on idempotency_key).
          2. Credits `rental_fee` straight into the lender's Wallet.
          3. Leaves `security_deposit` un-credited to anyone — it lives only
             in Payment.deposit_status = HELD until release/forfeit.
          4. Transitions the Booking APPROVED -> PAID.

        Returns the Payment instance.
        """
        # Idempotency short-circuit: if we've already processed this exact
        # client-generated key, return the existing result instead of
        # charging/crediting twice.
        existing = Payment.objects.select_for_update().filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

        booking = Booking.objects.select_for_update().get(pk=booking_id)

        if booking.renter_id != payer.id:
            raise EscrowError("Only the renter on this booking can pay.")
        if booking.status != Booking.Status.APPROVED:
            raise EscrowError(f"Booking is not awaiting payment (current status: {booking.status}).")
        if booking.is_payment_window_expired:
            raise EscrowError("The 48-hour payment window for this booking has expired.")

        try:
            GatewayClient.verify_payment(
                gateway_payment_id=gateway_payment_id,
                signature=gateway_signature,
                expected_amount=booking.total_price,
                raw_payload=raw_payload,
            )
        except GatewayError as exc:
            raise EscrowError(f"Payment verification failed: {exc}") from exc

        payment = Payment.objects.create(
            booking=booking,
            renter=booking.renter,
            lender=booking.lender,
            rental_fee=booking.rental_price,
            security_deposit=booking.deposit_amount,
            total_paid=booking.total_price,
            idempotency_key=idempotency_key,
            gateway_payment_id=gateway_payment_id,
            status=Payment.PaymentStatus.SUCCESS,
            deposit_status=Payment.DepositStatus.HELD,
            payout_released_at=timezone.now(),
        )

        # Split logic: rental fee flows to lender's wallet now. Deposit stays
        # in escrow (i.e. NOT in any wallet) until release/forfeit.
        EscrowService._credit_wallet(
            user=booking.lender,
            amount=payment.rental_fee,
            kind=WalletTransaction.Kind.RENTAL_PAYOUT,
            payment=payment,
        )

        try:
            transition_booking(booking_id=booking.pk, new_status=Booking.Status.PAID, actor=payer)
        except BookingStateError as exc:
            raise EscrowError(str(exc)) from exc

        return payment

    # ---- 2. Return confirmed -> release deposit --------------------------

    @staticmethod
    @transaction.atomic
    def release_deposit(*, booking_id, released_by):
        """
        Called from Booking Service's confirm_return step, AFTER the booking
        has already been moved to COMPLETED in the same outer transaction.
        Refunds the held security_deposit into the renter's wallet.
        """
        try:
            payment = Payment.objects.select_for_update().get(booking_id=booking_id)
        except Payment.DoesNotExist:
            raise EscrowError("No payment record found for this booking.")

        if payment.deposit_status != Payment.DepositStatus.HELD:
            # Already resolved (refunded/forfeited) — idempotent no-op.
            return payment

        EscrowService._credit_wallet(
            user=payment.renter,
            amount=payment.security_deposit,
            kind=WalletTransaction.Kind.DEPOSIT_REFUND,
            payment=payment,
        )

        payment.deposit_status = Payment.DepositStatus.REFUNDED
        payment.deposit_resolved_at = timezone.now()
        payment.save(update_fields=["deposit_status", "deposit_resolved_at", "updated_at"])
        return payment

    # ---- 3. Dispute resolution -> forfeit deposit to lender --------------

    @staticmethod
    @transaction.atomic
    def forfeit_deposit(*, booking_id, resolved_by, reason=""):
        """
        Admin/dispute-resolution path: pays the held deposit to the lender
        instead of refunding the renter (e.g. damaged item).
        """
        try:
            payment = Payment.objects.select_for_update().get(booking_id=booking_id)
        except Payment.DoesNotExist:
            raise EscrowError("No payment record found for this booking.")

        if payment.deposit_status != Payment.DepositStatus.HELD:
            return payment

        EscrowService._credit_wallet(
            user=payment.lender,
            amount=payment.security_deposit,
            kind=WalletTransaction.Kind.DEPOSIT_FORFEIT,
            payment=payment,
        )

        payment.deposit_status = Payment.DepositStatus.FORFEITED
        payment.deposit_resolved_at = timezone.now()
        payment.failure_reason = reason
        payment.save(update_fields=["deposit_status", "deposit_resolved_at", "failure_reason", "updated_at"])
        return payment

    # ---- internal helper ---------------------------------------------------

    @staticmethod
    def _credit_wallet(*, user, amount: Decimal, kind: str, payment: Payment):
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
        wallet.balance = wallet.balance + amount
        wallet.save(update_fields=["balance", "updated_at"])
        WalletTransaction.objects.create(
            wallet=wallet,
            payment=payment,
            kind=kind,
            amount=amount,
            balance_after=wallet.balance,
        )
        return wallet
