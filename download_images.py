import os
import django
import urllib.request
from urllib.error import HTTPError
from django.core.files.base import ContentFile
import urllib.parse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product

def get_keyword(product):
    # Try to extract a meaningful keyword
    name = product.name.lower()
    cat = product.category.lower()
    if 'camera' in name: return 'camera'
    if 'bike' in name or 'enfield' in name: return 'motorcycle'
    if 'car' in name or 'swift' in name: return 'car'
    if 'drone' in name: return 'drone'
    if 'iphone' in name or 'galaxy' in name or 'mobile' in name: return 'smartphone'
    if 'table' in name or 'chair' in name or 'furniture' in name: return 'furniture'
    if 'tent' in name or 'camping' in name: return 'camping'
    if 'tuxedo' in name or 'lehenga' in name or 'fashion' in name: return 'clothing'
    if 'drill' in name or 'washer' in name or 'tools' in name: return 'tools'
    if 'playstation' in name or 'ps5' in name: return 'playstation'
    if 'apartment' in name or 'space' in name: return 'apartment'
    if 'sewing' in name: return 'sewing'
    if 'printer' in name: return '3dprinter'
    if 'speaker' in name: return 'speaker'
    if 'racket' in name or 'badminton' in name: return 'badminton'
    if 'book' in name or 'harry potter' in name: return 'books'
    # Fallback to category word
    return urllib.parse.quote(product.category)

print("Downloading images for products...")
for p in Product.objects.all():
    kw = get_keyword(p)
    url = f"https://loremflickr.com/800/600/{kw}?lock={p.id}"
    print(f"[{p.id}] Fetching {url} for {p.name}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_content = response.read()
            filename = f"product_{p.id}_{kw}.jpg"
            p.image.save(filename, ContentFile(image_content), save=True)
            print(f" -> Saved {filename}")
    except Exception as e:
        print(f" -> Error downloading: {e}")

print("Done!")
