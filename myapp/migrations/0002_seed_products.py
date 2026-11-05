from django.db import migrations


PRODUCTS = [
    {
        "name": "The Sunday Lounge Chair",
        "slug": "sunday-lounge-chair",
        "category": "Living",
        "description": "A sculptural seat with soft curves and space to settle in.",
        "price": "489.00",
        "image_url": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85",
        "label": "Bestseller",
        "stock": 8,
    },
    {
        "name": "Aster Table Light",
        "slug": "aster-table-light",
        "category": "Lighting",
        "description": "A warm, gentle glow for slow evenings and quiet corners.",
        "price": "148.00",
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=85",
        "label": "Just in",
        "stock": 12,
    },
    {
        "name": "Morrow Ceramic Vase",
        "slug": "morrow-ceramic-vase",
        "category": "Objects",
        "description": "Hand-finished stoneware with a shape all its own.",
        "price": "64.00",
        "image_url": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?auto=format&fit=crop&w=900&q=85",
        "label": "",
        "stock": 20,
    },
    {
        "name": "The Everyday Throw",
        "slug": "everyday-throw",
        "category": "Textiles",
        "description": "A softly textured layer for the sofa, bed, or in-between.",
        "price": "96.00",
        "image_url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=900&q=85",
        "label": "",
        "stock": 15,
    },
    {
        "name": "Forma Side Table",
        "slug": "forma-side-table",
        "category": "Living",
        "description": "A little landing place for the things worth keeping close.",
        "price": "225.00",
        "image_url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=900&q=85",
        "label": "Small batch",
        "stock": 6,
    },
    {
        "name": "Soft Focus Candle",
        "slug": "soft-focus-candle",
        "category": "Objects",
        "description": "A clean, considered scent for the end of the day.",
        "price": "38.00",
        "image_url": "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?auto=format&fit=crop&w=900&q=85",
        "label": "",
        "stock": 24,
    },
]


def seed_products(apps, schema_editor):
    Product = apps.get_model("myapp", "Product")
    for product in PRODUCTS:
        Product.objects.get_or_create(slug=product["slug"], defaults=product)


def remove_seed_products(apps, schema_editor):
    Product = apps.get_model("myapp", "Product")
    Product.objects.filter(slug__in=[product["slug"] for product in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_products, remove_seed_products),
    ]
