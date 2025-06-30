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
            
            # More Vietnamese Beverages
            {'name': 'Café Sữa Đá G7', 'category': 'beverages', 'brand': 'G7', 'description': 'Vietnamese iced coffee with condensed milk'},
            {'name': 'Nước Cam Tipco 1L', 'category': 'beverages', 'brand': 'Tipco', 'description': 'Fresh orange juice'},
            {'name': 'Nước Mía Vinamit', 'category': 'beverages', 'brand': 'Vinamit', 'description': 'Sugarcane juice drink'},
            {'name': 'Trà Thanh Nhiệt Dr Thanh', 'category': 'beverages', 'brand': 'Dr Thanh', 'description': 'Herbal cooling tea'},
            {'name': 'Yakult Probiotics', 'category': 'beverages', 'brand': 'Yakult', 'description': 'Probiotic drink for digestion'},
            {'name': 'Nước Tăng Lực Warrior', 'category': 'beverages', 'brand': 'Warrior', 'description': 'Vietnamese energy drink'},
            {'name': 'Trà Đá Lipton 300ml', 'category': 'beverages', 'brand': 'Lipton', 'description': 'Iced tea ready to drink'},
            
            # More Vietnamese Snacks & Food
            {'name': 'Bánh Mì Sandwich Kinh Đô', 'category': 'food', 'brand': 'Kinh Đô', 'description': 'Vietnamese sandwich bread'},
            {'name': 'Mì Gói Hảo Hảo', 'category': 'food', 'brand': 'Acecook', 'description': 'Instant noodles, Vietnam\'s favorite'},
            {'name': 'Bánh Quy Cosy', 'category': 'snacks', 'brand': 'Cosy', 'description': 'Vietnamese biscuit brand'},
            {'name': 'Snack Oshi Corn', 'category': 'snacks', 'brand': 'Oshi', 'description': 'Corn snack with different flavors'},
            {'name': 'Mứt Tết Bibica', 'category': 'snacks', 'brand': 'Bibica', 'description': 'Vietnamese preserved fruit candy'},
            {'name': 'Bánh Tráng Phơi Sương', 'category': 'snacks', 'brand': 'Tây Ninh', 'description': 'Rice paper specialty from Tay Ninh'},
            {'name': 'Kẹo Dừa Bến Tre', 'category': 'snacks', 'brand': 'Bến Tre', 'description': 'Coconut candy from Ben Tre province'},
            
            # Ice Cream & Frozen
            {'name': 'Kem Cây Merino', 'category': 'food', 'brand': 'Merino', 'description': 'Popular Vietnamese ice cream brand'},
            {'name': 'Kem Tươi Wall\'s', 'category': 'food', 'brand': 'Wall\'s', 'description': 'International ice cream brand'},
            
            # Cigarettes (Very Common in Vietnamese Convenience Stores)
            {'name': 'Thuốc Lá Craven A', 'category': 'tobacco', 'brand': 'Craven A', 'description': 'Popular cigarette brand in Vietnam'},
            {'name': 'Thuốc Lá Marlboro', 'category': 'tobacco', 'brand': 'Marlboro', 'description': 'International cigarette brand'},
            {'name': 'Thuốc Lá Vinataba', 'category': 'tobacco', 'brand': 'Vinataba', 'description': 'Vietnamese tobacco brand'},
            
            # More Personal Care
            {'name': 'Sữa Tắm Romano', 'category': 'personal_care', 'brand': 'Romano', 'description': 'Popular men\'s body wash in Vietnam'},
            {'name': 'Dầu Gội Sunsilk', 'category': 'personal_care', 'brand': 'Sunsilk', 'description': 'Popular women\'s shampoo brand'},
            {'name': 'Kem Dưỡng Da Pond\'s', 'category': 'personal_care', 'brand': 'Pond\'s', 'description': 'Facial moisturizing cream'},
            {'name': 'Lăn Khử Mùi Rexona', 'category': 'personal_care', 'brand': 'Rexona', 'description': 'Roll-on deodorant'},
            {'name': 'Nước Rửa Tay Antibac', 'category': 'personal_care', 'brand': 'Antibac', 'description': 'Hand sanitizer, popular after COVID'},
            
            # Household Items
            {'name': 'Nước Rửa Chén Sunlight', 'category': 'household', 'brand': 'Sunlight', 'description': 'Dishwashing liquid'},
            {'name': 'Nước Giặt Omo', 'category': 'household', 'brand': 'Omo', 'description': 'Laundry detergent'},
            {'name': 'Khăn Ướt Bobby', 'category': 'household', 'brand': 'Bobby', 'description': 'Wet wipes for cleaning'},
            {'name': 'Túi Đựng Rác Saigon', 'category': 'household', 'brand': 'Saigon', 'description': 'Garbage bags'},
            
            # Stationery & Electronics
            {'name': 'Bút Bi Thiên Long', 'category': 'stationery', 'brand': 'Thiên Long', 'description': 'Popular Vietnamese pen brand'},
            {'name': 'Pin Panasonic AA', 'category': 'electronics', 'brand': 'Panasonic', 'description': 'AA batteries for devices'},
            {'name': 'Cáp Sạc USB Type-C', 'category': 'electronics', 'brand': 'Generic', 'description': 'USB charging cable'},
            {'name': 'Tai Nghe Bluetooth', 'category': 'electronics', 'brand': 'Generic', 'description': 'Wireless earphones'},
            
            # Medicines & Health
            {'name': 'Thuốc Cảm Cúm Decolgen', 'category': 'medicine', 'brand': 'Decolgen', 'description': 'Cold and flu medicine'},
            {'name': 'Dầu Nóng Thái Dương', 'category': 'medicine', 'brand': 'Thái Dương', 'description': 'Vietnamese medicated oil'},
            {'name': 'Thuốc Đau Bụng Smecta', 'category': 'medicine', 'brand': 'Smecta', 'description': 'Stomach ache medicine'},
            {'name': 'Vitamin C Redoxon', 'category': 'medicine', 'brand': 'Redoxon', 'description': 'Vitamin C supplement'},
            
            # Additional Food Items
            {'name': 'Bánh Mì Hamburger', 'category': 'food', 'brand': 'Kinh Đô', 'description': 'Hamburger buns'},
            {'name': 'Sữa Chua Vinamilk', 'category': 'food', 'brand': 'Vinamilk', 'description': 'Vietnamese yogurt'},
            {'name': 'Bánh Kẹp Chocolate', 'category': 'food', 'brand': 'Orion', 'description': 'Chocolate wafer sandwich'},
            {'name': 'Mì Ly Kokomi', 'category': 'food', 'brand': 'Kokomi', 'description': 'Cup noodles instant meal'},
            
            # Miscellaneous
            {'name': 'Que Tăm Chỉ Dental Floss', 'category': 'personal_care', 'brand': 'Generic', 'description': 'Dental floss picks'},
            {'name': 'Khẩu Trang Y Tế', 'category': 'personal_care', 'brand': 'Generic', 'description': 'Medical face masks'},
            {'name': 'Bao Tay Nhựa', 'category': 'household', 'brand': 'Generic', 'description': 'Disposable plastic gloves'},
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