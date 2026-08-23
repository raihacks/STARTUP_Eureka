from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Awaiting Lender Approval'),
        ('APPROVED', 'Approved (Awaiting Payment)'),
        ('PAID', 'Paid (Awaiting Handover)'),
        ('ACTIVE', 'Active (Item Handed Over)'),
        ('COMPLETED', 'Completed (Returned & Settled)'),
        ('REJECTED', 'Rejected by Lender'),
        ('CANCELLED', 'Cancelled'),
    ]

    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='renter_bookings', null=True)
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lender_bookings', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bookings')
    
    start_date = models.DateField()
    end_date = models.DateField()
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def platform_fee(self):
        return 100.00

    @property
    def total_amount(self):
        return float(self.rental_price) + float(self.security_deposit) + self.platform_fee