import os, re, django
from django.core.files import File
from App_Shop.models import Product, Category, AgeGroup, ClothingType

age_group, _ = AgeGroup.objects.get_or_create(name='Men')
clothing_type, _ = ClothingType.objects.get_or_create(name='Kameez Shalwar')
cat_eastern, _ = Category.objects.get_or_create(name='Eastern Wear')

base_dir = r"c:\Users\Qadri Laptop\Downloads\Archive\static\img\product\Eastern Collection"

products_dict = {}
for file in os.listdir(base_dir):
    if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        continue
    name_no_ext = os.path.splitext(file)[0]
    base_name = re.sub(r'\s*angle\s*\d+$', '', name_no_ext, flags=re.IGNORECASE).strip()
    if base_name not in products_dict:
        products_dict[base_name] = []
    products_dict[base_name].append(os.path.join(base_dir, file))

for name, images in products_dict.items():
    images = sorted(images)
    display_name = name.title()
    print(f"Seeding: {display_name} ({len(images)} images)")
    product, created = Product.objects.get_or_create(
        name=display_name,
        defaults={
            'preview_text': f'Premium {display_name} from our Eastern Wear collection.',
            'detail_text': f'Elevate your style with our {display_name}. Crafted from premium cotton for ultimate comfort and a refined look.',
            'price': 2500.00,
            'old_price': 3200.00,
            'age_group': age_group,
            'category': cat_eastern,
            'clothing_type': clothing_type,
        }
    )
    if created:
        with open(images[0], 'rb') as f:
            product.mainimage.save(os.path.basename(images[0]), File(f), save=False)
        if len(images) > 1:
            with open(images[1], 'rb') as f:
                product.image2.save(os.path.basename(images[1]), File(f), save=False)
        if len(images) > 2:
            with open(images[2], 'rb') as f:
                product.image3.save(os.path.basename(images[2]), File(f), save=False)
        product.save()
        print(f"  [OK] Created")
    else:
        print(f"  - Already exists")

print("Eastern Collection seeding complete!")
