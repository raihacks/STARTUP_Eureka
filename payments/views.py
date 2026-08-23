import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from bookings.utils import check_and_expire_booking

from .gateway import GatewayClient
from .services import EscrowError, EscrowService


@login_required
def pay_booking(request, booking_id):
    """
    Simulated Web Checkout Page.
    GET: Renders payment sheet with itemized costs & simulated UPI/Card PIN input.
    POST: Validates dummy PIN, auto-generates unique simulation gateway IDs, and processes escrow.
    """
    booking = get_object_or_404(Booking, pk=booking_id, renter=request.user)
    check_and_expire_booking(booking)

    if booking.status != Booking.Status.APPROVED:
        messages.error(request, "This booking is not currently awaiting payment.")
        return redirect("customer_catalog")

    if request.method == "POST":
        pin = request.POST.get("pin", "").strip()

        # Simulate PIN validation (accepts '1234' or any valid 4-digit PIN)
        if not pin or len(pin) != 4 or not pin.isdigit():
            messages.error(request, "Invalid payment PIN. Please enter a valid 4-digit PIN (e.g., 1234).")
            return render(request, "payments/pay_booking.html", {"booking": booking})

        # Generate unique transaction IDs dynamically to prevent database UNIQUE constraint errors
        idempotency_key = request.POST.get("idempotency_key") or uuid.uuid4().hex
        gateway_payment_id = request.POST.get("gateway_payment_id") or f"PAY_SIM_{uuid.uuid4().hex[:10].upper()}"
        gateway_signature = request.POST.get("gateway_signature") or f"SIG_SIM_{uuid.uuid4().hex[:10].upper()}"
        gateway_order_id = request.POST.get("gateway_order_id") or f"ORD_SIM_{uuid.uuid4().hex[:8].upper()}"

        try:
            EscrowService.process_payment(
                booking_id=booking.pk,
                payer=request.user,
                idempotency_key=idempotency_key,
                gateway_payment_id=gateway_payment_id,
                gateway_signature=gateway_signature,
                raw_payload={
                    "order_id": gateway_order_id,
                    "amount": str(booking.total_price),
                    "simulated": True,
                },
            )
            messages.success(request, "Payment successful! Your rental is confirmed and the deposit is secured in escrow.")
            return redirect("customer_catalog")
        except EscrowError as exc:
            messages.error(request, str(exc))
            return redirect("customer_catalog")

    return render(request, "payments/pay_booking.html", {"booking": booking})