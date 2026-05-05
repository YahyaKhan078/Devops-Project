import os
import re
import django
import shutil
from django.conf import settings
from App_Shop.models import Product, Category, AgeGroup, ClothingType
from django.core.files import File

# Ensure AgeGroup and ClothingType exist
age_group, _ = AgeGroup.objects.get_or_create(name='Men')
clothing_type, _ = ClothingType.objects.get_or_create(name='General')

# Create Categories
cat_casual, _ = Category.objects.get_or_create(name='Casual Wear')
cat_formal, _ = Category.objects.get_or_create(name='Formal')
cat_eastern, _ = Category.objects.get_or_create(name='Eastern Wear')

def get_category(folder_name):
    if folder_name in ['Baggy Jeans', 'Polo Shirts', 'Shorts', 'Slim Jeans', 'Tee Shirts', 'Trousers', 'new  arrivals']:
        return cat_casual
    elif folder_name in ['Coats', 'Dress Pants']:
        return cat_formal
    else:
        return cat_eastern

base_dir = r"c:\Users\Qadri Laptop\Downloads\Archive\static\img\product"

products_dict = {}

for root, dirs, files in os.walk(base_dir):
    folder_name = os.path.basename(root)
    if folder_name == 'product':
        continue
    
    category = get_category(folder_name)
    
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            # Extract base name
            # e.g., "Baggy Men's Jeans1.webp" -> "Baggy Men's Jeans"
            # e.g., "Slogan Print Polo Shirt Angle 1.jpg" -> "Slogan Print Polo Shirt"
            
            name_without_ext = os.path.splitext(file)[0]
            
            # Remove trailing numbers or "Angle X"
            base_name = re.sub(r'(?i)\s*Angle\s*\d+$', '', name_without_ext)
            base_name = re.sub(r'\s*\d+$', '', base_name)
            base_name = base_name.strip().strip('.')
            
            key = f"{folder_name}_{base_name}"
            
            if key not in products_dict:
                products_dict[key] = {
                    'name': base_name,
                    'category': category,
                    'images': []
                }
            
            products_dict[key]['images'].append(os.path.join(root, file))

# Create products
for key, data in products_dict.items():
    name = data['name']
    category = data['category']
    images = sorted(data['images']) # Sort to try to get 1, 2, 3 in order
    
    if not images:
        continue
        
    print(f"Processing {name} with {len(images)} images")
    
    # Create or update product
    product, created = Product.objects.get_or_create(
        name=name,
        defaults={
            'preview_text': f"Premium {name} from our {category.name} collection.",
            'detail_text': f"Elevate your style with our {name}. Carefully crafted for maximum comfort and durability.",
            'price': 1500.00, # Default price
            'old_price': 1800.00,
            'age_group': age_group,
            'category': category,
            'clothing_type': clothing_type,
        }
    )
    
    # We need to save the images to the media directory 'Products'
    # Django's ImageField handles this when we assign a File object
    with open(images[0], 'rb') as f:
        product.mainimage.save(os.path.basename(images[0]), File(f), save=False)
        
    if len(images) > 1:
        with open(images[1], 'rb') as f:
            product.image2.save(os.path.basename(images[1]), File(f), save=False)
            
    if len(images) > 2:
        with open(images[2], 'rb') as f:
            product.image3.save(os.path.basename(images[2]), File(f), save=False)
            
    product.save()

print("Product seeding complete!")
