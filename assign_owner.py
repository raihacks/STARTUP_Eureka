import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

# Create a profile where requests will go (must be a LENDER to manage requests)
owner, created = User.objects.get_or_create(
    username='item_owner',
    defaults={
        'email': 'owner@example.com',
        'role': 'LENDER',
        'kyc_status': 'VERIFIED'
    }
)
if created:
    owner.set_password('password123')
    owner.save()

# Assign all products to this owner
updated_count = Product.objects.all().update(owner=owner)
print(f"Assigned {updated_count} products to {owner.username} (Password: password123).")

# Also create a renter profile to make the requests from
renter, created2 = User.objects.get_or_create(
    username='item_renter',
    defaults={
        'email': 'renter@example.com',
        'role': 'RENTER',
        'kyc_status': 'VERIFIED'
    }
)
if created2:
    renter.set_password('password123')
    renter.save()
print(f"Created a renter profile to make requests from: {renter.username} (Password: password123).")
