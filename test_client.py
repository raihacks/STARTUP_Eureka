import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from products.models import Product
from bookings.models import Booking
from datetime import date, timedelta

User = get_user_model()
Booking.objects.all().delete()
Product.objects.all().delete()
User.objects.all().delete()

lender = User.objects.create_user(username='lender_test', password='pwd')
lender.role = 'LENDER'
lender.save()

renter = User.objects.create_user(username='renter_test', password='pwd')
renter.role = 'CUSTOMER'
renter.save()

product = Product.objects.create(
    owner=lender,
    name='Test Item',
    rental_price=10.00,
    security_deposit=50.00,
    location='Test City'
)

c = Client()
c.login(username='renter_test', password='pwd')
start = date.today()
end = start + timedelta(days=2)

print(f"Creating booking for product {product.id} from {start} to {end}")
resp = c.post(f'/booking/create/{product.id}/', {'start_date': start.strftime('%Y-%m-%d'), 'end_date': end.strftime('%Y-%m-%d')}, follow=True)
print("Redirect to / status:", resp.status_code)

bookings = Booking.objects.all()
print("Total bookings:", bookings.count())
for b in bookings:
    print(f"Booking {b.id} status: {b.status}")

# Check customer catalog page
resp = c.get('/product/catalog/')
print("Customer page status:", resp.status_code)
if 'Test Item' in resp.content.decode('utf-8') and 'Pending' in resp.content.decode('utf-8') or 'Requested' in resp.content.decode('utf-8'):
    print("Found booking in customer page")

# Check lender page
c.logout()
c.login(username='lender_test', password='pwd')
resp = c.get('/product/lender/products/')
print("Lender page status:", resp.status_code)
content = resp.content.decode('utf-8')
if 'Test Item' in content and 'renter_test' in content:
    print("Found booking in lender page html")
else:
    print("Did NOT find booking in lender page html")

