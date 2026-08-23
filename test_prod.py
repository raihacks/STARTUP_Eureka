import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
user, created = User.objects.get_or_create(username='testauth', defaults={'password': 'password123', 'role': 'RENTER'})
if created:
    user.set_password('password123')
    user.save()

c = Client()
c.login(username='testauth', password='password123')

resp = c.get('/product/catalog/')
print("Catalog status:", resp.status_code)
if resp.status_code == 500:
    print(resp.content)
