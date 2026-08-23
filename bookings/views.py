from datetime import datetime
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from .models import Booking

# 1. RENTER: Creates request from /product/catalog/
def create_booking(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()
        
        days = (end_date - start_date).days or 1
        rental_total = product.rental_price * days

        Booking.objects.create(
            renter=request.user,
            lender=product.owner,  # Ensure Product model has 'owner'
            product=product,
            start_date=start_date,
            end_date=end_date,
            rental_price=rental_total,
            security_deposit=product.security_deposit,
            status='REQUESTED'
        )
        messages.success(request, "Booking requested! Waiting for lender to accept.")
        return redirect('customer_catalog')

    return redirect('customer_catalog')


# 2. LENDER: Accepts or Rejects request
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, lender=request.user)
    booking.status = 'APPROVED'
    booking.save()
    messages.success(request, f"Booking #{booking.id} accepted. Renter can now pay within 2 days.")
    return redirect('lender_products')

def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, lender=request.user)
    booking.status = 'REJECTED'
    booking.save()
    messages.info(request, f"Booking #{booking.id} rejected.")
    return redirect('lender_products')


# 3. LENDER: Confirms Handover (Item given to renter)
def confirm_handover(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, lender=request.user)
    if booking.status == 'PAID':
        booking.status = 'ACTIVE'
        booking.save()
        messages.success(request, "Rental period active. Item handed over to renter.")
    return redirect('lender_products')


# 4. LENDER: Confirms Return (Triggers payout settlement)
def confirm_return(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, lender=request.user)
    if booking.status == 'ACTIVE':
        booking.status = 'COMPLETED'
        booking.save()
        # MVP Payout Settlement Simulation:
        # 1. Rental Amount (₹1,000) released to Lender
        # 2. Deposit Amount (₹5,000) refunded to Renter
        # 3. Platform Fee (₹100) retained
        messages.success(request, f"Item returned! Released ₹{booking.rental_price} to you and refunded ₹{booking.security_deposit} deposit to renter.")
    return redirect('lender_products')

