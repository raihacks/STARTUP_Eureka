import requests
import time
import subprocess
import threading

def run_server():
    subprocess.run(['.venv/bin/python', 'manage.py', 'runserver', '8080'])

# Install Django 5.1
subprocess.run(['.venv/bin/pip', 'install', 'Django==5.1'])

# Start server
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

time.sleep(3) # Wait for server to start

session = requests.Session()

# 1. Create a user manually in db
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
from products.models import Product
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

# 2. Login
resp = session.get('http://127.0.0.1:8080/accounts/login/')
csrftoken = resp.cookies['csrftoken']
resp = session.post('http://127.0.0.1:8080/accounts/login/', data={
    'username': 'renter',
    'password': 'pwd',
    'csrfmiddlewaretoken': csrftoken
}, headers={'Referer': 'http://127.0.0.1:8080/accounts/login/'})

print("Login status:", resp.status_code)

# 3. Create booking
resp = session.get('http://127.0.0.1:8080/product/catalog/')
csrftoken = resp.cookies['csrftoken']
from datetime import date, timedelta
start = date.today()
end = start + timedelta(days=2)

resp = session.post(f'http://127.0.0.1:8080/booking/create/{product.id}/', data={
    'start_date': start.strftime('%Y-%m-%d'),
    'end_date': end.strftime('%Y-%m-%d'),
    'csrfmiddlewaretoken': csrftoken
}, headers={'Referer': 'http://127.0.0.1:8080/product/catalog/'})

print("Booking status:", resp.status_code)

from bookings.models import Booking
bookings = Booking.objects.all()
print("Bookings count:", bookings.count())
for b in bookings:
    print(f"Booking {b.id} status: {b.status}")

# 4. Check lender page
session.cookies.clear()
resp = session.get('http://127.0.0.1:8080/accounts/login/')
csrftoken = resp.cookies['csrftoken']
session.post('http://127.0.0.1:8080/accounts/login/', data={
    'username': 'lender',
    'password': 'pwd',
    'csrfmiddlewaretoken': csrftoken
}, headers={'Referer': 'http://127.0.0.1:8080/accounts/login/'})

resp = session.get('http://127.0.0.1:8080/product/lender/products/')
print("Lender page status:", resp.status_code)
if 'Test Item' in resp.text and 'renter' in resp.text:
    print("Found booking in lender page html")
else:
    print("Did NOT find booking in lender page html")

