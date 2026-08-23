import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product
from bookings.models import Booking
from bookings.utils import create_booking_request
from datetime import date, timedelta

User = get_user_model()
User.objects.all().delete()
Product.objects.all().delete()

lender = User.objects.create_user(username='lender', password='pwd')
renter = User.objects.create_user(username='renter', password='pwd')

product = Product.objects.create(
    owner=lender,
    name='Test Item',
    rental_price=10.00,
    security_deposit=50.00,
    location='Test City'
)

start = date.today()
end = start + timedelta(days=2)

try:
    booking = create_booking_request(product=product, renter=renter, start_date=start, end_date=end)
    print("Booking created successfully:", booking.id)
except Exception as e:
    print("Error creating booking:", str(e))

print("Bookings for lender:")
all_bookings = Booking.objects.filter(product__owner=lender).order_by('-id')
active_requests = all_bookings.exclude(
    status__iexact='COMPLETED'
).exclude(
    status__iexact='REJECTED'
).exclude(
    status__iexact='CANCELLED'
)

print("Active requests count:", active_requests.count())
for r in active_requests:
    print("Request:", r.id, r.status, r.renter.username, r.product.name)
