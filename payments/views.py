from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from bookings.models import Booking
from bookings.utils import check_and_expire_booking

@login_required
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, renter=request.user)

    # Prevent payment if 2 days have elapsed
    if check_and_expire_booking(booking) or booking.status.upper() == 'EXPIRED':
        messages.error(request, "The 2-day payment deadline has passed. This booking is expired.")
        return redirect('customer_catalog')  # adjust if using namespace like 'products:customer_catalog'

    # Process payment
    if booking.status.upper() == 'APPROVED':
        booking.status = 'PAID'
        booking.save()
        
        # Mark product unavailable while rented
        booking.product.available = False
        booking.product.save()
        
        messages.success(request, "Payment successful! Your order is ready for handover.")

    return redirect('customer_catalog')