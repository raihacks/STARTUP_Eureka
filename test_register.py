import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

c = Client()
resp = c.post('/accounts/register/', {
    'username': 'newuser123',
    'password': 'password123',
    'password_confirm': 'password123',
    'email': 'newuser@test.com',
    'role': 'RENTER',
})
print("Register response:", resp.status_code)
if resp.status_code == 500:
    print("500 error:", resp.content)
elif resp.status_code == 200:
    print("Form errors:", resp.context['form'].errors)
