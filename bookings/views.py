from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .models import Booking, BookingStateError
from .permissions import require_lender, require_renter
from .utils import OverlapError, create_booking_request, transition_booking


@login_required
def create_booking(request, product_id):
    """
    POST target for the "Confirm & Request Rental" form in the customer
    catalog modal. Matches the JS-constructed action `/booking/create/<id>/`.
    """
    product = get_object_or_404(Product, pk=product_id, available=True)

    if request.method != "POST":
        return redirect("customer_catalog")

    try:
        start_date = datetime.strptime(request.POST["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.POST["end_date"], "%Y-%m-%d").date()
    except (KeyError, ValueError):
        messages.error(request, "Please provide valid start and end dates.")
        return redirect("customer_catalog")

    try:
        create_booking_request(
            product=product,
            renter=request.user,
            start_date=start_date,
            end_date=end_date,
        )
        messages.success(request, "Rental request sent! You'll be notified once the lender responds.")
    except OverlapError as exc:
        messages.error(request, str(exc))
    except ValueError as exc:
        messages.error(request, str(exc))

    return redirect("customer_catalog")


@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    require_lender(booking, request.user)

    if request.method != "POST":
        return redirect("lender_products")

    try:
        with transaction.atomic():
            transition_booking(
                booking_id=booking.pk,
                new_status=Booking.Status.APPROVED,
                actor=request.user,
            )
        messages.success(request, "Booking approved. The customer has 48 hours to pay.")
    except BookingStateError as exc:
        messages.error(request, str(exc))

    return redirect("lender_products")


@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    require_lender(booking, request.user)

    if request.method != "POST":
        return redirect("lender_products")

    try:
        with transaction.atomic():
            transition_booking(
                booking_id=booking.pk,
                new_status=Booking.Status.REJECTED,
                actor=request.user,
            )
        messages.info(request, "Booking request declined.")
    except BookingStateError as exc:
        messages.error(request, str(exc))

    return redirect("lender_products")


@login_required
def confirm_handover(request, booking_id):
    """PAID -> ACTIVE. Also flips Product.available = False."""
    booking = get_object_or_404(Booking, pk=booking_id)
    require_lender(booking, request.user)

    if request.method != "POST":
        return redirect("lender_products")

    try:
        with transaction.atomic():
            transition_booking(
                booking_id=booking.pk,
                new_status=Booking.Status.ACTIVE,
                actor=request.user,
            )
            Product.objects.filter(pk=booking.product_id).update(available=False)
        messages.success(request, "Handover confirmed. Item marked as rented.")
    except BookingStateError as exc:
        messages.error(request, str(exc))

    return redirect("lender_products")


@login_required
def confirm_return(request, booking_id):
    """
    ACTIVE -> COMPLETED. Relists the item, then hands off to the
    Payment & Escrow Service to release the deposit.
    """
    booking = get_object_or_404(Booking, pk=booking_id)
    require_lender(booking, request.user)

    if request.method != "POST":
        return redirect("lender_products")

    from payments.services import EscrowService  # local import: avoid app coupling at load time

    try:
        with transaction.atomic():
            transition_booking(
                booking_id=booking.pk,
                new_status=Booking.Status.COMPLETED,
                actor=request.user,
            )
            Product.objects.filter(pk=booking.product_id).update(available=True)
            EscrowService.release_deposit(booking_id=booking.pk, released_by=request.user)
        messages.success(request, "Return confirmed. Deposit released back to the customer.")
    except BookingStateError as exc:
        messages.error(request, str(exc))

    return redirect("lender_products")
