"""
Django management command to seed product catalog.
Part 3: Product catalog with random generated items for convenience stores.

Usage: python manage.py seed_products
"""

from django.core.management.base import BaseCommand
import random

from backend.apps.stores.models import Item


class Command(BaseCommand):
    help = 'Seed the database with convenience store product catalog'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=None,
            help='Number of products to generate (default: use predefined list)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing products...')
            Item.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing products cleared'))

        count = options.get('count')
        if count:
            self.stdout.write(f'📦 Generating {count} random products...')
            items = self.generate_random_products(count)
        else:
            self.stdout.write('📦 Seeding predefined product catalog...')
            items = self.seed_predefined_products()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully seeded {len(items)} products')
        )

    def seed_predefined_products(self):
        """Create predefined product catalog with realistic Vietnamese convenience store products."""
        items_data = [
            # Vietnamese Beverages - Most Popular
            {'name': 'Trà Ô Long Tea+ 500ml', 'category': 'beverages', 'brand': 'Tea+', 'description': 'Oolong tea drink, very popular in Vietnam'},
            {'name': 'Number 1 Energy Drink 330ml', 'category': 'beverages', 'brand': 'Number 1', 'description': 'Vietnamese energy drink'},
            {'name': 'Sting Energy Drink 330ml', 'category': 'beverages', 'brand': 'Sting', 'description': 'Popular energy drink in Vietnam'},
            {'name': 'Aquafina Water 500ml', 'category': 'beverages', 'brand': 'Aquafina', 'description': 'Purified drinking water'},
            {'name': 'Coca-Cola 330ml', 'category': 'beverages', 'brand': 'Coca-Cola', 'description': 'Classic cola drink'},
            {'name': 'Trà Xanh C2 455ml', 'category': 'beverages', 'brand': 'C2', 'description': 'Green tea with jasmine flavor'},
            
            # Vietnamese Snacks - Very Popular
            {'name': 'Lays Potato Chips', 'category': 'snacks', 'brand': 'Lays', 'description': 'Classic potato chips, popular in Vietnam'},
            {'name': 'Phồng Tôm Calbee', 'category': 'snacks', 'brand': 'Calbee', 'description': 'Shrimp crackers, Vietnamese favorite'},
            {'name': 'Oishi Snack', 'category': 'snacks', 'brand': 'Oishi', 'description': 'Popular Vietnamese snack brand'},
            {'name': 'Mì Hảo Hảo Tôm Chua Cay', 'category': 'snacks', 'brand': 'Acecook', 'description': 'Spicy sour shrimp instant noodles'},
            {'name': 'Orion Choco Pie', 'category': 'snacks', 'brand': 'Orion', 'description': 'Soft cake with chocolate and marshmallow'},
            {'name': 'Bánh Tráng Nướng', 'category': 'snacks', 'brand': 'Tân Hương', 'description': 'Grilled rice paper, Vietnamese street snack'},
            
            # Essential Personal Care
            {'name': 'Kem Đánh Răng P/S', 'category': 'personal_care', 'brand': 'P/S', 'description': 'Popular Vietnamese toothpaste brand'},
            {'name': 'Dầu Gội Clear Men', 'category': 'personal_care', 'brand': 'Clear', 'description': 'Anti-dandruff shampoo for men'},
            {'name': 'Xà Phòng Lifebuoy', 'category': 'personal_care', 'brand': 'Lifebuoy', 'description': 'Antibacterial soap bar'},
            {'name': 'Khăn Giấy Tempo', 'category': 'household', 'brand': 'Tempo', 'description': 'Facial tissue paper'},
            
            # Common Health/Medicine
            {'name': 'Thuốc Đau Đầu Panadol', 'category': 'other', 'brand': 'Panadol', 'description': 'Headache relief medicine'},
            {'name': 'Nước Súc Miệng Listerine', 'category': 'personal_care', 'brand': 'Listerine', 'description': 'Mouthwash for oral care'},
            
            # Convenience Items
            {'name': 'Bao Cao Su Durex', 'category': 'personal_care', 'brand': 'Durex', 'description': 'Condoms, commonly sold in convenience stores'},
            {'name': 'Bật Lửa Gas', 'category': 'other', 'brand': 'Generic', 'description': 'Gas lighter, essential item'},
        ]

        # Create Item objects
        items = []
        for item_data in items_data:
            item, created = Item.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            items.append(item)
            if created:
                self.stdout.write(f'Created item: {item.name}')
            else:
                self.stdout.write(f'Item already exists: {item.name}')

        return items

    def generate_random_products(self, count):
        """Generate random products for testing purposes."""
        categories = ['beverages', 'snacks', 'household', 'personal_care', 'other']
        brands = [
            'Generic', 'Premium', 'Value', 'Fresh', 'Quality', 'Daily', 'Essential',
            'Eco', 'Natural', 'Organic', 'Quick', 'Easy', 'Pro', 'Max', 'Ultra'
        ]
        
        product_types = {
            'beverages': ['Water', 'Juice', 'Soda', 'Tea', 'Coffee', 'Energy Drink', 'Milk'],
            'snacks': ['Chips', 'Cookies', 'Candy', 'Crackers', 'Nuts', 'Chocolate', 'Gum'],
            'household': ['Cleaner', 'Detergent', 'Soap', 'Paper', 'Sponge', 'Brush', 'Spray'],
            'personal_care': ['Shampoo', 'Cream', 'Lotion', 'Deodorant', 'Toothpaste', 'Razor'],
            'other': ['Batteries', 'Lighter', 'Pen', 'Bandage', 'Medicine', 'Charger']
        }
        
        items = []
        for i in range(count):
            category = random.choice(categories)
            product_type = random.choice(product_types[category])
            brand = random.choice(brands)
            
            name = f"{brand} {product_type} {random.randint(1, 999)}"
            description = f"High quality {product_type.lower()} from {brand}"
            
            item_data = {
                'name': name,
                'category': category,
                'brand': brand,
                'description': description
            }
            
            item, created = Item.objects.get_or_create(
                name=name,
                defaults=item_data
            )
            items.append(item)
            
            if created:
                self.stdout.write(f'Created random item: {item.name}')
        
        return items 