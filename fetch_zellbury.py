import requests
from bs4 import BeautifulSoup
import urllib.request
import os
import django
import sys

sys.path.append('c:\\Users\\Qadri Laptop\\Downloads\\Archive')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_website_django.settings')
django.setup()

from App_Shop.models import Product
from django.conf import settings

url = 'https://zellbury.com/collections/men'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.content, 'html.parser')

images = soup.find_all('img')
urls = []
for img in images:
    src = img.get('src') or img.get('data-src') or img.get('data-srcset')
    if src:
        src = src.split(',')[0].split(' ')[0]
        if 'cdn.shopify.com' in src and ('jpg' in src or 'webp' in src):
            if src.startswith('//'):
                src = 'https:' + src
            if '?' in src:
                src = src.split('?')[0] # Remove query params
            urls.append(src)

urls = list(set(urls))

# Separate banners and products
banners = [u for u in urls if '2000' in u or '1032' in u] # Hero banner usually wide
products_urls = [u for u in urls if u not in banners]

if len(banners) == 0:
    banners = urls[:4]
    products_urls = urls[4:]

# Make sure we have enough
if len(banners) < 4:
    banners.extend(products_urls[:4-len(banners)])
    products_urls = products_urls[4-len(banners):]

# Save collections to static
static_img_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
names = ['hero-banner.png', 'collection-casual.png', 'collection-formal.png', 'collection-summer.png']
for url, name in zip(banners[:4], names):
    urllib.request.urlretrieve(url, os.path.join(static_img_dir, name))
    print(f'Downloaded {name}')

# Save products to media and update DB
products = Product.objects.all().order_by('id')[:5]
for i, product in enumerate(products):
    file_path = os.path.join(settings.MEDIA_ROOT, 'Products', f'zellbury_{i}.jpg')
    urllib.request.urlretrieve(products_urls[i], file_path)
    product.mainimage = f'Products/zellbury_{i}.jpg'
    product.save()
    print(f'Updated product {product.name}')

print("Successfully applied Zellbury images.")
