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
    # VEHICLES
    dict(
        name="Royal Enfield Classic 350",
        category=Product.Category.VEHICLES,
        description="Well-maintained Classic 350, serviced monthly. Ideal for weekend rides or short-term commuting. Helmet included.",
        rental_price=900,
        security_deposit=8000,
        location="Andheri East, Mumbai",
        condition="Good",
    ),
    dict(
        name="Maruti Suzuki Swift 2022",
        category=Product.Category.VEHICLES,
        description="Reliable hatchback with excellent AC and smooth manual transmission. Perfect for weekend getaways.",
        rental_price=2000,
        security_deposit=15000,
        location="Bandra West, Mumbai",
        condition="Excellent",
    ),

    # ELECTRONICS
    dict(
        name="Canon EOS R6 Mirrorless Camera",
        category=Product.Category.ELECTRONICS,
        description="Full-frame mirrorless camera with 20MP sensor, in-body stabilization, and 4K video. Comes with 24-105mm kit lens, extra battery, and 64GB card.",
        rental_price=1500,
        security_deposit=15000,
        location="Bandra West, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="DJI Mavic Air 2 Drone",
        category=Product.Category.ELECTRONICS,
        description="4K drone with obstacle avoidance and 34-min flight time. Great for events, real estate shoots, or travel content.",
        rental_price=1200,
        security_deposit=12000,
        location="Powai, Mumbai",
        condition="Excellent",
    ),

    # MOBILES
    dict(
        name="iPhone 14 Pro (128GB)",
        category=Product.Category.MOBILES,
        description="Unlocked iPhone 14 Pro in great condition, screen protector and case applied since day one. Comes with original charger and box.",
        rental_price=600,
        security_deposit=20000,
        location="Lower Parel, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="Samsung Galaxy S23 Ultra",
        category=Product.Category.MOBILES,
        description="Pristine condition S23 Ultra with S-Pen. Amazing camera for concerts or events. Includes fast charger.",
        rental_price=650,
        security_deposit=22000,
        location="Juhu, Mumbai",
        condition="Excellent",
    ),

    # FURNITURE
    dict(
        name="IKEA 6-Seater Dining Table Set",
        category=Product.Category.FURNITURE,
        description="Solid wood 6-seater dining set, perfect for short-term stays or events. Minor wear on legs, otherwise sturdy and clean.",
        rental_price=400,
        security_deposit=3000,
        location="Malad West, Mumbai",
        condition="Good",
    ),
    dict(
        name="Ergonomic Office Chair",
        category=Product.Category.FURNITURE,
        description="High-back mesh ergonomic chair with lumbar support. Perfect for WFH setups or temporary office needs.",
        rental_price=150,
        security_deposit=1500,
        location="Navi Mumbai",
        condition="Excellent",
    ),

    # FASHION
    dict(
        name="Designer Lehenga (Red & Gold)",
        category=Product.Category.FASHION,
        description="Heavy bridal/party lehenga worn only once. Comes with matching blouse and dupatta. Alterations possible.",
        rental_price=2500,
        security_deposit=10000,
        location="Santacruz, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="Men's Navy Blue Tuxedo",
        category=Product.Category.FASHION,
        description="Premium tailored navy blue tuxedo, size 40R. Perfect for weddings, galas, and formal events.",
        rental_price=1200,
        security_deposit=5000,
        location="Colaba, Mumbai",
        condition="Good",
    ),

    # BOOKS_SPORTS
    dict(
        name="Yonex Astrox 99 Badminton Racket",
        category=Product.Category.BOOKS_SPORTS,
        description="Professional grade badminton racket with fresh BG65 titanium stringing. Includes grip tape.",
        rental_price=100,
        security_deposit=2000,
        location="Dadar, Mumbai",
        condition="Good",
    ),
    dict(
        name="Harry Potter Complete Book Set",
        category=Product.Category.BOOKS_SPORTS,
        description="Complete set of 7 Harry Potter books (Hardcover). Great for a weekend reading marathon.",
        rental_price=150,
        security_deposit=1500,
        location="Borivali, Mumbai",
        condition="Excellent",
    ),

    # TOOLS
    dict(
        name="Bosch Cordless Drill Machine",
        category=Product.Category.TOOLS,
        description="18V cordless drill with 2 batteries, charger, and a 20-piece bit set. Great for home renovation or furniture assembly.",
        rental_price=250,
        security_deposit=1500,
        location="Thane West, Thane",
        condition="Excellent",
    ),
    dict(
        name="Heavy Duty Pressure Washer",
        category=Product.Category.TOOLS,
        description="1500W high-pressure washer for cleaning cars, driveways, or patios. Includes all nozzles and extension cord.",
        rental_price=400,
        security_deposit=3000,
        location="Vashi, Navi Mumbai",
        condition="Good",
    ),

    # OUTDOORS
    dict(
        name="4-Person Camping Tent (Quechua)",
        category=Product.Category.OUTDOORS,
        description="Waterproof 4-person dome tent, easy 2-minute setup. Includes rainfly and ground sheet. Used on 3 trips, no leaks or tears.",
        rental_price=350,
        security_deposit=2000,
        location="Navi Mumbai",
        condition="Good",
    ),
    dict(
        name="Portable BBQ Grill",
        category=Product.Category.OUTDOORS,
        description="Charcoal BBQ grill with folding legs. Includes basic grilling tools. Perfect for picnics or terrace parties.",
        rental_price=200,
        security_deposit=1000,
        location="Goregaon, Mumbai",
        condition="Good",
    ),

    # ENTERTAINMENT
    dict(
        name="PlayStation 5 Console + 2 Controllers",
        category=Product.Category.ENTERTAINMENT,
        description="PS5 disc edition with two DualSense controllers and three games (FIFA 24, Spider-Man 2, God of War Ragnarok). Perfect for events or parties.",
        rental_price=800,
        security_deposit=10000,
        location="Juhu, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="Sony Party Speaker (SRS-XP700)",
        category=Product.Category.ENTERTAINMENT,
        description="Massive party speaker with omnidirectional sound, deep bass, and LED lights. 25-hour battery life.",
        rental_price=1000,
        security_deposit=8000,
        location="Chembur, Mumbai",
        condition="Excellent",
    ),

    # PROPERTIES
    dict(
        name="Sea-facing Studio Apartment",
        category=Product.Category.PROPERTIES,
        description="Furnished studio with a sea view, fast Wi-Fi, and workspace. Perfect for short-term rental or a weekend staycation.",
        rental_price=3500,
        security_deposit=10000,
        location="Worli, Mumbai",
        condition="Excellent",
    ),
    dict(
        name="Commercial Event Space / Hall",
        category=Product.Category.PROPERTIES,
        description="1000 sq ft hall with basic seating and AC. Ideal for workshops, small exhibitions, or pop-up stores.",
        rental_price=5000,
        security_deposit=15000,
        location="Andheri West, Mumbai",
        condition="Good",
    ),

    # OTHER
    dict(
        name="Industrial Sewing Machine",
        category=Product.Category.OTHER,
        description="Heavy-duty Juki sewing machine suitable for denim and leather. Good for short-term fashion projects.",
        rental_price=400,
        security_deposit=5000,
        location="Kurla, Mumbai",
        condition="Good",
    ),
    dict(
        name="3D Printer (Creality Ender 3)",
        category=Product.Category.OTHER,
        description="Entry-level 3D printer. Filament not included (bring your own PLA/PETG). Great for prototyping.",
        rental_price=300,
        security_deposit=4000,
        location="Powai, Mumbai",
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