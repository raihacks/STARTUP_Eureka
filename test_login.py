import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
User.objects.all().delete()
user = User.objects.create_user(username='testuser', password='password123', role='RENTER')

c = Client()
# Log in
logged_in = c.login(username='testuser', password='password123')
print("Logged in:", logged_in)

# Access dashboard
response = c.get('/accounts/dashboard/')
print("Dashboard response:", response.status_code)
if response.status_code == 302:
    print("Dashboard redirects to:", response.url)
    resp2 = c.get(response.url)
    print("Redirect response:", resp2.status_code)
    if resp2.status_code == 500:
        print(resp2.content)
elif response.status_code == 500:
    print(response.content)

# Test register
resp = c.post('/accounts/register/', {
    'username': 'newuser',
    'password': 'password123',
    'password_confirm': 'password123',
    'email': 'test@test.com',
    'role': 'RENTER',
})
print("Register response:", resp.status_code)
if resp.status_code == 500:
    print("Register 500 error:", resp.content)
