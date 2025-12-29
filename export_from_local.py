import os
import sys
import django

# Point to your Django project
sys.path.append('C:/ecommerce-full-stack/Django-Ecommerce-main/ecom')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')

# Temporarily set database to local PostgreSQL
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PASSWORD'] = 'monsterx001'

django.setup()

from store.models import Category, Product
from django.contrib.auth.models import User
from store.models import Profile
from payment.models import ShippingAddress
import json

print("Exporting data from LOCAL PostgreSQL...")

# Export Categories
categories_data = []
for cat in Category.objects.all():
    categories_data.append({
        'id': cat.id,
        'name': cat.name,
    })
print(f"✅ Exported {len(categories_data)} categories")

# Export Products
products_data = []
for prod in Product.objects.all():
    products_data.append({
        'id': prod.id,
        'name': prod.name,
        'price': float(prod.price),
        'category_id': prod.category.id,
        'description': prod.description,
        'image': prod.image.name if prod.image else '',
        'is_sale': prod.is_sale,
        'sale_price': float(prod.sale_price),
    })
print(f"✅ Exported {len(products_data)} products")

# Export Users
users_data = []
for user in User.objects.all():
    users_data.append({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })
print(f"✅ Exported {len(users_data)} users")

# Export Profiles
profiles_data = []
for profile in Profile.objects.all():
    profiles_data.append({
        'user_id': profile.user.id,
        'phone': profile.phone,
        'address1': profile.address1,
        'address2': profile.address2,
        'city': profile.city,
        'state': profile.state,
        'zipcode': profile.zipcode,
        'country': profile.country,
    })
print(f"✅ Exported {len(profiles_data)} profiles")

# Save to JSON
data = {
    'categories': categories_data,
    'products': products_data,
    'users': users_data,
    'profiles': profiles_data,
}

with open('exported_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\n🎉 Export complete! File: exported_data.json")
print(f"Total: {len(categories_data)} categories, {len(products_data)} products, {len(users_data)} users")