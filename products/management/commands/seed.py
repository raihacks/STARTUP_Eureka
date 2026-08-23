"""
Seeds sample Product rows for local testing.

Usage:
    python manage.py seed_products

Assigns all products to the first available user (or a user you specify
with --username). If no users exist, create one first:
    python manage.py createsuperuser
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from products.models import  Product

User = get_user_model()

SAMPLE_PRODUCTS = [
    dict(
        name="Canon EOS R6 Mirrorless Camera",
        category=Product.Category.ELECTRONICS,
        description="Full-frame mirrorless camera with 20MP sensor, in-body stabilization, "
                     "and 4K video. Comes with 24-105mm kit lens, extra battery, and 64GB card.",
        rental_price=1500,
        security_deposit=15000,
        location="Bandra West, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="Royal Enfield Classic 350",
        category=Product.Category.VEHICLES,
        description="Well-maintained Classic 350, serviced monthly. Ideal for weekend rides "
                     "or short-term commuting. Helmet included.",
        rental_price=900,
        security_deposit=8000,
        location="Andheri East, Mumbai",
        condition="Good",
    ),
    dict(
        name="DJI Mavic Air 2 Drone",
        category=Product.Category.ELECTRONICS,
        description="4K drone with obstacle avoidance and 34-min flight time. Great for "
                     "events, real estate shoots, or travel content.",
        rental_price=1200,
        security_deposit=12000,
        location="Powai, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="IKEA 6-Seater Dining Table Set",
        category=Product.Category.FURNITURE,
        description="Solid wood 6-seater dining set, perfect for short-term stays or events. "
                     "Minor wear on legs, otherwise sturdy and clean.",
        rental_price=400,
        security_deposit=3000,
        location="Malad West, Mumbai",
        condition="Good",
    ),
    dict(
        name="Bosch Cordless Drill Machine",
        category=Product.Category.TOOLS,
        description="18V cordless drill with 2 batteries, charger, and a 20-piece bit set. "
                     "Great for home renovation or furniture assembly.",
        rental_price=250,
        security_deposit=1500,
        location="Thane West, Thane",
        condition="Excellent",
    ),
    dict(
        name="4-Person Camping Tent (Quechua)",
        category=Product.Category.OUTDOORS,
        description="Waterproof 4-person dome tent, easy 2-minute setup. Includes rainfly and "
                     "ground sheet. Used on 3 trips, no leaks or tears.",
        rental_price=350,
        security_deposit=2000,
        location="Navi Mumbai",
        condition="Good",
    ),
    dict(
        name="PlayStation 5 Console + 2 Controllers",
        category=Product.Category.ENTERTAINMENT,
        description="PS5 disc edition with two DualSense controllers and three games "
                     "(FIFA 24, Spider-Man 2, God of War Ragnarok). Perfect for events or parties.",
        rental_price=800,
        security_deposit=10000,
        location="Juhu, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="iPhone 14 Pro (128GB)",
        category=Product.Category.MOBILES,
        description="Unlocked iPhone 14 Pro in great condition, screen protector and case "
                     "applied since day one. Comes with original charger and box.",
        rental_price=600,
        security_deposit=20000,
        location="Lower Parel, Mumbai",
        condition="Excellent",
    ),
]


class Command(BaseCommand):
    help = "Seed sample Product listings for local development/testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Username to assign as the owner of seeded products. "
                 "Defaults to the first user found.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing products before seeding.",
        )

    def handle(self, *args, **options):
        if options["username"]:
            try:
                owner = User.objects.get(username=options["username"])
            except User.DoesNotExist:
                raise CommandError(f"No user found with username '{options['username']}'.")
        else:
            owner = User.objects.first()
            if owner is None:
                raise CommandError(
                    "No users exist yet. Run 'python manage.py createsuperuser' first."
                )

        if options["clear"]:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing product(s)."))

        created = 0
        for data in SAMPLE_PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                name=data["name"],
                owner=owner,
                defaults=data,
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} new product(s) (owner: {owner.username}). "
                f"Total products now: {Product.objects.count()}"
            )
        )