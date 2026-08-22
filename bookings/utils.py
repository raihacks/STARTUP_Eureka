from datetime import timedelta
from django.utils import timezone

def check_and_expire_booking(booking):
    """Expires booking if 48 hours pass without payment and releases the product."""
    payment_deadline = booking.created_at + timedelta(days=2)
    
    if timezone.now() > payment_deadline and booking.status.upper() == 'APPROVED':
        booking.status = 'EXPIRED'
        booking.save()
        
        # Relist product to catalog
        booking.product.available = True
        booking.product.save()
        return True
    return False