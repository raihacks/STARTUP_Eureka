import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample products and users'

    def handle(self, *args, **kwargs):
        # 1. Ensure a lender user exists
        lender, created = User.objects.get_or_create(
            username='sample_lender',
            defaults={
                'email': 'lender@example.com',
                'role': 'LENDER',
                'kyc_status': 'VERIFIED'
            }
        )
        if created:
            lender.set_password('password123')
            lender.save()
            self.stdout.write(self.style.SUCCESS(f'Created sample lender: {lender.username}'))

        # 2. Ensure a renter user exists
        renter, created = User.objects.get_or_create(
            username='sample_renter',
            defaults={
                'email': 'renter@example.com',
                'role': 'RENTER',
                'kyc_status': 'VERIFIED'
            }
        )
        if created:
            renter.set_password('password123')
            renter.save()
            self.stdout.write(self.style.SUCCESS(f'Created sample renter: {renter.username}'))

        # 3. Create Sample Products
        sample_products = [
            # Vehicles
            {'name': 'Honda City 2020', 'description': 'Well maintained sedan.', 'category': 'Vehicles', 'rental_price': 1500.0, 'security_deposit': 10000.0, 'location': 'Mumbai', 'condition': 'Good', 'available': True},
            {'name': 'Royal Enfield Classic 350', 'description': 'Cruiser bike.', 'category': 'Vehicles', 'rental_price': 800.0, 'security_deposit': 5000.0, 'location': 'Pune', 'condition': 'Excellent', 'available': True},
            {'name': 'Ford EcoSport 2018', 'description': 'Compact SUV.', 'category': 'Vehicles', 'rental_price': 1200.0, 'security_deposit': 8000.0, 'location': 'Delhi', 'condition': 'Good', 'available': True},
            {'name': 'TVS Jupiter Scooter', 'description': 'Easy city commute.', 'category': 'Vehicles', 'rental_price': 400.0, 'security_deposit': 2000.0, 'location': 'Bangalore', 'condition': 'Used', 'available': True},
            # Electronics
            {'name': 'Sony A7III Camera', 'description': 'Full-frame mirrorless.', 'category': 'Electronics', 'rental_price': 2500.0, 'security_deposit': 15000.0, 'location': 'Mumbai', 'condition': 'Excellent', 'available': True},
            {'name': 'LG 55-inch 4K TV', 'description': 'Smart TV.', 'category': 'Electronics', 'rental_price': 800.0, 'security_deposit': 5000.0, 'location': 'Chennai', 'condition': 'Good', 'available': True},
            {'name': 'Bosch Washing Machine', 'description': 'Front load 7kg.', 'category': 'Electronics', 'rental_price': 500.0, 'security_deposit': 4000.0, 'location': 'Delhi', 'condition': 'Used', 'available': True},
            {'name': 'JBL PartyBox 310', 'description': 'Bluetooth party speaker.', 'category': 'Electronics', 'rental_price': 600.0, 'security_deposit': 3000.0, 'location': 'Goa', 'condition': 'Excellent', 'available': True},
            # Mobiles
            {'name': 'iPhone 13 Pro Max', 'description': '256GB Sierra Blue.', 'category': 'Mobiles', 'rental_price': 1200.0, 'security_deposit': 20000.0, 'location': 'Pune', 'condition': 'Like New', 'available': True},
            {'name': 'Samsung Galaxy S22 Ultra', 'description': 'With S-Pen.', 'category': 'Mobiles', 'rental_price': 1100.0, 'security_deposit': 18000.0, 'location': 'Bangalore', 'condition': 'Excellent', 'available': True},
            {'name': 'iPad Pro 12.9"', 'description': 'M1 Chip, 128GB.', 'category': 'Mobiles', 'rental_price': 900.0, 'security_deposit': 15000.0, 'location': 'Mumbai', 'condition': 'Good', 'available': True},
            {'name': 'OnePlus 11 5G', 'description': '16GB RAM, 256GB.', 'category': 'Mobiles', 'rental_price': 700.0, 'security_deposit': 10000.0, 'location': 'Delhi', 'condition': 'Like New', 'available': True},
            # Furniture
            {'name': 'Wooden Dining Table', 'description': '6-seater solid wood.', 'category': 'Furniture', 'rental_price': 300.0, 'security_deposit': 2000.0, 'location': 'Kolkata', 'condition': 'Used', 'available': True},
            {'name': 'Ergonomic Office Chair', 'description': 'High back with headrest.', 'category': 'Furniture', 'rental_price': 150.0, 'security_deposit': 1000.0, 'location': 'Bangalore', 'condition': 'Good', 'available': True},
            {'name': '3-Seater Sofa', 'description': 'Fabric sofa, grey color.', 'category': 'Furniture', 'rental_price': 400.0, 'security_deposit': 3000.0, 'location': 'Mumbai', 'condition': 'Good', 'available': True},
            {'name': 'Queen Size Bed Frame', 'description': 'Metal bed frame.', 'category': 'Furniture', 'rental_price': 250.0, 'security_deposit': 1500.0, 'location': 'Pune', 'condition': 'Used', 'available': True},
            # Fashion
            {'name': 'Designer Wedding Lehenga', 'description': 'Sabyasachi inspired.', 'category': 'Fashion', 'rental_price': 5000.0, 'security_deposit': 25000.0, 'location': 'Delhi', 'condition': 'Excellent', 'available': True},
            {'name': 'Men\'s Tuxedo Suit', 'description': 'Black slim fit tuxedo.', 'category': 'Fashion', 'rental_price': 1500.0, 'security_deposit': 5000.0, 'location': 'Mumbai', 'condition': 'Good', 'available': True},
            {'name': 'Gucci Handbag', 'description': 'Original leather bag.', 'category': 'Fashion', 'rental_price': 2000.0, 'security_deposit': 15000.0, 'location': 'Bangalore', 'condition': 'Excellent', 'available': True},
            {'name': 'Traditional Sherwani', 'description': 'Silk sherwani.', 'category': 'Fashion', 'rental_price': 3000.0, 'security_deposit': 10000.0, 'location': 'Jaipur', 'condition': 'Good', 'available': True},
            # Books & Sports
            {'name': 'Harry Potter Complete Set', 'description': 'All 7 books.', 'category': 'Books & Sports', 'rental_price': 100.0, 'security_deposit': 500.0, 'location': 'Chennai', 'condition': 'Good', 'available': True},
            {'name': 'Kookaburra Cricket Bat', 'description': 'English willow.', 'category': 'Books & Sports', 'rental_price': 300.0, 'security_deposit': 2000.0, 'location': 'Mumbai', 'condition': 'Used', 'available': True},
            {'name': 'Yonex Badminton Racket', 'description': 'Carbon graphite.', 'category': 'Books & Sports', 'rental_price': 150.0, 'security_deposit': 1000.0, 'location': 'Pune', 'condition': 'Excellent', 'available': True},
            {'name': 'Trek Mountain Bike', 'description': '21-gear bicycle.', 'category': 'Books & Sports', 'rental_price': 400.0, 'security_deposit': 3000.0, 'location': 'Bangalore', 'condition': 'Good', 'available': True}
        ]

        products_created = 0
        for p_data in sample_products:
            # Check if product exists by name to avoid duplicates
            if not Product.objects.filter(name=p_data['name']).exists():
                Product.objects.create(owner=lender, **p_data)
                products_created += 1
                
        if products_created > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully added {products_created} sample products.'))
        else:
            self.stdout.write(self.style.WARNING('Sample products already exist in the database. Skipped.'))
            
        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
