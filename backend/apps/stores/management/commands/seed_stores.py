"""
Django management command to seed stores from JSON file.
Part 2: Stores with coordinates that auto-detect districts and generate addresses.

Usage: python manage.py seed_stores [--stores-file stores.json]
"""

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from decimal import Decimal
import random
import json

from backend.apps.stores.models import District, Store
from .seed_utils import (
    detect_district_from_coordinates,
    generate_address_from_coordinates, 
    get_stores_json_path
)


def detect_store_type_from_name(name):
    """Detect store type from store name based on brand patterns."""
    name_lower = name.lower()
    
    if name.startswith('7-Eleven') or '7-eleven' in name_lower:
        return '7-eleven'
    elif name.startswith('MINISTOP') or 'ministop' in name_lower:
        return 'ministop'
    elif name.startswith('WinMart') or name.startswith('WIN ') or 'winmart' in name_lower:
        return 'winmart'
    elif name.startswith('Circle K') or 'circle k' in name_lower:
        return 'circle-k'
    elif name.startswith('FamilyMart') or 'familymart' in name_lower:
        return 'familymart'
    elif name.startswith('GS25') or 'gs25' in name_lower:
        return 'gs25'
    elif name.startswith('Bách hóa XANH') or name.startswith('Bách Hóa Xanh') or 'bách hóa xanh' in name_lower:
        return 'bach-hoa-xanh'
    elif name.startswith('Co.opXtra') or 'co.opxtra' in name_lower or 'coopxtra' in name_lower:
        return 'coopxtra'
    elif name.startswith('Satrafoods') or 'satrafoods' in name_lower:
        return 'satrafoods'
    else:
        return 'other'


class Command(BaseCommand):
    help = 'Seed the database with stores from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing stores before seeding',
        )
        parser.add_argument(
            '--stores-file',
            type=str,
            default='stores.json',
            help='JSON file containing store data (default: stores.json)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing stores...')
            Store.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing stores cleared'))

        stores_file = options.get('stores_file', 'stores.json')
        self.stdout.write(f'🏪 Seeding stores from {stores_file}...')
        stores = self.seed_stores_from_json(stores_file)
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully seeded {len(stores)} stores')
        )

    def seed_stores_from_json(self, stores_file):
        """Create stores from JSON file with name, longitude, latitude."""
        stores_path = get_stores_json_path(stores_file)
        
        try:
            with open(stores_path, 'r', encoding='utf-8') as f:
                stores_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Stores JSON file not found: {stores_path}'))
            self.stdout.write(self.style.WARNING('Creating sample stores.json file...'))
            self._create_sample_stores_file(stores_path)
            return []
        
        if not isinstance(stores_data, list):
            self.stdout.write(self.style.ERROR('Stores JSON must be an array of store objects'))
            return []
        
        # Check if districts exist
        if not District.objects.exists():
            self.stdout.write(self.style.ERROR('No districts found. Please run: python manage.py seed_districts'))
            return []
        
        stores = []
        
        for i, store_data in enumerate(stores_data):
            try:
                # Required fields
                name = store_data.get('name')
                longitude = store_data.get('longitude') or store_data.get('lng')
                latitude = store_data.get('latitude') or store_data.get('lat')
                
                if not all([name, longitude, latitude]):
                    self.stdout.write(self.style.WARNING(f'Skipping store {i+1}: missing required fields (name, longitude, latitude)'))
                    continue
                
                # Convert to numbers
                longitude = float(longitude)
                latitude = float(latitude)
                
                # Auto-detect district from coordinates
                district = detect_district_from_coordinates(longitude, latitude, self.stdout)
                if not district:
                    self.stdout.write(self.style.WARNING(f'Skipping store {name}: could not determine district'))
                    continue
                
                # Generate address
                address = generate_address_from_coordinates(longitude, latitude, district.name)
                
                # Auto-detect store type from name, or use provided type
                store_type = store_data.get('type', detect_store_type_from_name(name))
                phone = store_data.get('phone', f"+84-{random.randint(28, 99)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}")
                email = store_data.get('email', f"store{i+1}@{name.split()[0].lower()}.com")
                opening_hours = store_data.get('opening_hours', f"{random.randint(6, 8)}:00-{random.randint(21, 23)}:00")
                rating = store_data.get('rating', round(random.uniform(3.5, 5.0), 1))
                is_active = store_data.get('is_active', True)
                
                # Create store
                store_obj_data = {
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'email': email,
                    'store_type': store_type,
                    'district': district.name,
                    'district_obj': district,
                    'city': 'Ho Chi Minh City',
                    'opening_hours': opening_hours,
                    'is_active': is_active,
                    'rating': Decimal(str(rating)),
                    'location': Point(longitude, latitude, srid=4326)
                }
                
                store, created = Store.objects.get_or_create(
                    name=name,
                    defaults=store_obj_data
                )
                stores.append(store)
                
                if created:
                    self.stdout.write(f'Created store: {store.name} ({store_type}) in {district.name}')
                else:
                    self.stdout.write(f'Store already exists: {store.name}')
                    
            except (ValueError, TypeError) as e:
                self.stdout.write(self.style.WARNING(f'Skipping store {i+1}: invalid data - {e}'))
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating store {i+1}: {e}'))
                continue
        
        return stores

    def _create_sample_stores_file(self, stores_path):
        """Create a sample stores.json file for reference."""
        sample_stores = [
            {
                "name": "FamilyMart Nguyen Hue",
                "longitude": 106.7020,
                "latitude": 10.7770,
                "phone": "+84-28-123-4567",
                "opening_hours": "06:00-23:00",
                "rating": 4.5
            },
            {
                "name": "Circle K District 3",
                "longitude": 106.6868,
                "latitude": 10.7869
            },
            {
                "name": "7-Eleven Phu My Hung",
                "longitude": 106.7200,
                "latitude": 10.7320,
                "email": "store@7eleven.vn"
            },
            {
                "name": "WinMart Go Vap",
                "longitude": 106.6650,
                "latitude": 10.8380,
                "is_active": True
            }
        ]
        
        try:
            with open(stores_path, 'w', encoding='utf-8') as f:
                json.dump(sample_stores, f, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f'Created sample {stores_path}'))
            self.stdout.write('Please edit the file with your store data and run the command again.')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Could not create sample file: {e}')) 