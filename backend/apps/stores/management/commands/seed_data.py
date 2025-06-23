"""
Django management command to seed the database with Ho Chi Minh City data.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon
from decimal import Decimal
import random

from backend.apps.stores.models import District, Store, Inventory


class Command(BaseCommand):
    help = 'Seed the database with Ho Chi Minh City districts, stores, and inventory data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            District.objects.all().delete()
            Store.objects.all().delete()
            Inventory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        self.stdout.write('Seeding Ho Chi Minh City data...')
        
        # Create districts
        districts = self.create_districts()
        
        # Create stores
        stores = self.create_stores(districts)
        
        # Create inventory
        self.create_inventory(stores)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded data: {len(districts)} districts, '
                f'{len(stores)} stores, and inventory items'
            )
        )

    def create_districts(self):
        """Create Ho Chi Minh City districts with realistic boundaries."""
        districts_data = [
            {
                'name': 'District 1',
                'code': 'D1',
                'city': 'Ho Chi Minh City',
                'population': 204899,
                'area_km2': Decimal('7.73'),
                'district_type': 'urban',
                'avg_income': Decimal('45000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.6900, 10.7600),
                    (106.7200, 10.7600),
                    (106.7200, 10.8000),
                    (106.6900, 10.8000),
                    (106.6900, 10.7600),
                ], srid=4326)
            },
            {
                'name': 'District 3',
                'code': 'D3',
                'city': 'Ho Chi Minh City',
                'population': 188945,
                'area_km2': Decimal('4.92'),
                'district_type': 'urban',
                'avg_income': Decimal('42000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.6800, 10.7800),
                    (106.7100, 10.7800),
                    (106.7100, 10.8200),
                    (106.6800, 10.8200),
                    (106.6800, 10.7800),
                ], srid=4326)
            },
            {
                'name': 'Binh Thanh',
                'code': 'BT',
                'city': 'Ho Chi Minh City',
                'population': 499164,
                'area_km2': Decimal('20.76'),
                'district_type': 'urban',
                'avg_income': Decimal('38000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.7000, 10.8000),
                    (106.7500, 10.8000),
                    (106.7500, 10.8500),
                    (106.7000, 10.8500),
                    (106.7000, 10.8000),
                ], srid=4326)
            },
            {
                'name': 'Phu Nhuan',
                'code': 'PN',
                'city': 'Ho Chi Minh City',
                'population': 163961,
                'area_km2': Decimal('4.88'),
                'district_type': 'urban',
                'avg_income': Decimal('40000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.6700, 10.7900),
                    (106.7000, 10.7900),
                    (106.7000, 10.8300),
                    (106.6700, 10.8300),
                    (106.6700, 10.7900),
                ], srid=4326)
            },
            {
                'name': 'Tan Binh',
                'code': 'TB',
                'city': 'Ho Chi Minh City',
                'population': 430436,
                'area_km2': Decimal('22.38'),
                'district_type': 'urban',
                'avg_income': Decimal('35000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.6500, 10.7800),
                    (106.7000, 10.7800),
                    (106.7000, 10.8300),
                    (106.6500, 10.8300),
                    (106.6500, 10.7800),
                ], srid=4326)
            },
            {
                'name': 'District 7',
                'code': 'D7',
                'city': 'Ho Chi Minh City',
                'population': 360155,
                'area_km2': Decimal('35.69'),
                'district_type': 'suburban',
                'avg_income': Decimal('50000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.7200, 10.7200),
                    (106.7800, 10.7200),
                    (106.7800, 10.7800),
                    (106.7200, 10.7800),
                    (106.7200, 10.7200),
                ], srid=4326)
            },
            {
                'name': 'District 2',
                'code': 'D2',
                'city': 'Ho Chi Minh City',
                'population': 147168,
                'area_km2': Decimal('49.74'),
                'district_type': 'suburban',
                'avg_income': Decimal('55000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.7500, 10.7800),
                    (106.8000, 10.7800),
                    (106.8000, 10.8300),
                    (106.7500, 10.8300),
                    (106.7500, 10.7800),
                ], srid=4326)
            },
            {
                'name': 'Thu Duc',
                'code': 'TD',
                'city': 'Ho Chi Minh City',
                'population': 592686,
                'area_km2': Decimal('47.76'),
                'district_type': 'suburban',
                'avg_income': Decimal('42000000'),
                'is_active': True,
                'boundary': Polygon([
                    (106.7500, 10.8300),
                    (106.8000, 10.8300),
                    (106.8000, 10.8800),
                    (106.7500, 10.8800),
                    (106.7500, 10.8300),
                ], srid=4326)
            }
        ]

        districts = []
        for data in districts_data:
            district, created = District.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            districts.append(district)
            if created:
                self.stdout.write(f'Created district: {district.name}')
            else:
                self.stdout.write(f'District already exists: {district.name}')

        return districts

    def create_stores(self, districts):
        """Create convenience stores across Ho Chi Minh City."""
        store_chains = [
            'Circle K', 'FamilyMart', '7-Eleven', 'GS25', 'Mini Stop',
            'VinMart+', 'Bach Hoa Xanh', 'Co.op Food', 'Satrafoods'
        ]
        
        store_types = ['convenience', 'mini-mart', 'supermarket']
        
        # Store locations across HCM City (realistic coordinates)
        store_locations = [
            # District 1
            (106.7000, 10.7700, 'District 1'),
            (106.7100, 10.7800, 'District 1'),
            (106.7050, 10.7750, 'District 1'),
            (106.7150, 10.7850, 'District 1'),
            
            # District 3
            (106.6900, 10.7900, 'District 3'),
            (106.7000, 10.8000, 'District 3'),
            (106.6950, 10.7950, 'District 3'),
            
            # Binh Thanh
            (106.7200, 10.8200, 'Binh Thanh'),
            (106.7300, 10.8300, 'Binh Thanh'),
            (106.7250, 10.8250, 'Binh Thanh'),
            (106.7350, 10.8350, 'Binh Thanh'),
            
            # Phu Nhuan
            (106.6800, 10.8000, 'Phu Nhuan'),
            (106.6900, 10.8100, 'Phu Nhuan'),
            (106.6850, 10.8050, 'Phu Nhuan'),
            
            # Tan Binh
            (106.6700, 10.8000, 'Tan Binh'),
            (106.6800, 10.8100, 'Tan Binh'),
            (106.6750, 10.8050, 'Tan Binh'),
            (106.6850, 10.8150, 'Tan Binh'),
            
            # District 7
            (106.7300, 10.7300, 'District 7'),
            (106.7400, 10.7400, 'District 7'),
            (106.7350, 10.7350, 'District 7'),
            (106.7450, 10.7450, 'District 7'),
            
            # District 2
            (106.7600, 10.8000, 'District 2'),
            (106.7700, 10.8100, 'District 2'),
            (106.7650, 10.8050, 'District 2'),
            
            # Thu Duc
            (106.7600, 10.8400, 'Thu Duc'),
            (106.7700, 10.8500, 'Thu Duc'),
            (106.7650, 10.8450, 'Thu Duc'),
            (106.7750, 10.8550, 'Thu Duc'),
        ]

        stores = []
        for i, (lng, lat, district_name) in enumerate(store_locations):
            # Find the district
            district = next((d for d in districts if d.name == district_name), districts[0])
            
            # Generate store data
            store_name = f"{random.choice(store_chains)} - {district_name} #{i+1}"
            store_type = random.choice(store_types)
            
            # Generate realistic address
            street_names = ['Nguyen Hue', 'Le Loi', 'Dong Khoi', 'Pasteur', 'Vo Van Tan', 'Truong Dinh']
            street_name = random.choice(street_names)
            street_number = random.randint(1, 200)
            
            store_data = {
                'name': store_name,
                'address': f"{street_number} {street_name}, {district_name}, Ho Chi Minh City",
                'phone': f"+84-{random.randint(28, 99)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                'email': f"store{i+1}@{store_name.split()[0].lower()}.com",
                'store_type': store_type,
                'district': district_name,
                'district_obj': district,
                'city': 'Ho Chi Minh City',
                'opening_hours': f"{random.randint(6, 8)}:00-{random.randint(21, 23)}:00",
                'is_active': True,
                'rating': Decimal(str(round(random.uniform(3.5, 5.0), 1))),
                'location': Point(lng, lat, srid=4326)
            }
            
            store, created = Store.objects.get_or_create(
                name=store_name,
                defaults=store_data
            )
            stores.append(store)
            
            if created:
                self.stdout.write(f'Created store: {store.name}')
            else:
                self.stdout.write(f'Store already exists: {store.name}')

        return stores

    def create_inventory(self, stores):
        """Create inventory items for all stores."""
        inventory_items = [
            # Beverages
            {'item_name': 'Coca-Cola 330ml', 'unit': 'cans', 'price': Decimal('8000'), 'category': 'beverages'},
            {'item_name': 'Pepsi 330ml', 'unit': 'cans', 'price': Decimal('8000'), 'category': 'beverages'},
            {'item_name': 'Red Bull 250ml', 'unit': 'cans', 'price': Decimal('12000'), 'category': 'beverages'},
            {'item_name': 'Coffee 3-in-1', 'unit': 'packets', 'price': Decimal('3000'), 'category': 'beverages'},
            {'item_name': 'Green Tea 500ml', 'unit': 'bottles', 'price': Decimal('15000'), 'category': 'beverages'},
            {'item_name': 'Orange Juice 1L', 'unit': 'bottles', 'price': Decimal('25000'), 'category': 'beverages'},
            
            # Snacks
            {'item_name': 'Pringles Original', 'unit': 'cans', 'price': Decimal('35000'), 'category': 'snacks'},
            {'item_name': 'Lay\'s Classic', 'unit': 'bags', 'price': Decimal('15000'), 'category': 'snacks'},
            {'item_name': 'Oreo Cookies', 'unit': 'packs', 'price': Decimal('25000'), 'category': 'snacks'},
            {'item_name': 'M&M\'s Chocolate', 'unit': 'bags', 'price': Decimal('20000'), 'category': 'snacks'},
            {'item_name': 'Instant Noodles', 'unit': 'packets', 'price': Decimal('8000'), 'category': 'snacks'},
            {'item_name': 'Potato Chips', 'unit': 'bags', 'price': Decimal('12000'), 'category': 'snacks'},
            
            # Household
            {'item_name': 'Toothpaste', 'unit': 'tubes', 'price': Decimal('25000'), 'category': 'household'},
            {'item_name': 'Shampoo 400ml', 'unit': 'bottles', 'price': Decimal('45000'), 'category': 'household'},
            {'item_name': 'Soap Bar', 'unit': 'bars', 'price': Decimal('15000'), 'category': 'household'},
            {'item_name': 'Tissue Paper', 'unit': 'rolls', 'price': Decimal('8000'), 'category': 'household'},
            {'item_name': 'Laundry Detergent', 'unit': 'packs', 'price': Decimal('35000'), 'category': 'household'},
            {'item_name': 'Dish Soap', 'unit': 'bottles', 'price': Decimal('20000'), 'category': 'household'},
            
            # Personal Care
            {'item_name': 'Deodorant', 'unit': 'cans', 'price': Decimal('30000'), 'category': 'personal_care'},
            {'item_name': 'Razor Blades', 'unit': 'packs', 'price': Decimal('25000'), 'category': 'personal_care'},
            {'item_name': 'Face Cream', 'unit': 'tubes', 'price': Decimal('40000'), 'category': 'personal_care'},
            {'item_name': 'Sunscreen SPF 50', 'unit': 'bottles', 'price': Decimal('60000'), 'category': 'personal_care'},
            
            # Health
            {'item_name': 'Paracetamol 500mg', 'unit': 'packs', 'price': Decimal('15000'), 'category': 'health'},
            {'item_name': 'Vitamin C 1000mg', 'unit': 'bottles', 'price': Decimal('80000'), 'category': 'health'},
            {'item_name': 'Band-Aids', 'unit': 'boxes', 'price': Decimal('12000'), 'category': 'health'},
            {'item_name': 'Hand Sanitizer', 'unit': 'bottles', 'price': Decimal('25000'), 'category': 'health'},
        ]

        for store in stores:
            # Each store gets a random selection of items
            store_items = random.sample(inventory_items, random.randint(15, 25))
            
            for item_data in store_items:
                # Randomize quantity and availability
                quantity = random.randint(10, 100)
                is_available = random.choice([True, True, True, False])  # 75% chance of being available
                
                inventory_data = {
                    'store': store,
                    'item_name': item_data['item_name'],
                    'quantity': quantity,
                    'unit': item_data['unit'],
                    'price': item_data['price'],
                    'category': item_data['category'],
                    'is_available': is_available
                }
                
                inventory, created = Inventory.objects.get_or_create(
                    store=store,
                    item_name=item_data['item_name'],
                    defaults=inventory_data
                )
                
                if created:
                    self.stdout.write(f'Created inventory: {inventory.item_name} at {store.name}') 