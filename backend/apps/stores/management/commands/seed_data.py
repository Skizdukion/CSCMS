"""
Django management command to seed the database with Ho Chi Minh City data.
Main coordinator command that runs individual seed parts.

Usage: 
  python manage.py seed_data                    # Run all parts
  python manage.py seed_data --part 1           # Run only districts
  python manage.py seed_data --part 2           # Run only stores
  python manage.py seed_data --part 3           # Run only products  
  python manage.py seed_data --part 4           # Run only inventory
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from backend.apps.stores.models import District, Store, Item, Inventory


class Command(BaseCommand):
    help = 'Seed the database with Ho Chi Minh City districts, stores, and inventory data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--part',
            type=int,
            choices=[1, 2, 3, 4],
            help='Run specific part: 1=districts, 2=stores, 3=products, 4=inventory',
        )
        parser.add_argument(
            '--districts-only',
            action='store_true',
            help='Seed only districts data (same as --part 1)',
        )
        parser.add_argument(
            '--stores-file',
            type=str,
            default='stores.json',
            help='JSON file containing store data (default: stores.json)',
        )

    def handle(self, *args, **options):
        # Handle legacy --districts-only flag
        if options['districts_only']:
            options['part'] = 1
        
        # Determine which parts to run
        part = options.get('part')
        stores_file = options.get('stores_file', 'stores.json')
        clear = options.get('clear', False)
        
        if clear:
            self.stdout.write('🗑️  Clearing existing data...')
            if part is None or part >= 4:
                Inventory.objects.all().delete()
                self.stdout.write('   Cleared inventory data')
            if part is None or part >= 3:
                Item.objects.all().delete()
                self.stdout.write('   Cleared item data')
            if part is None or part >= 2:
                Store.objects.all().delete()
                self.stdout.write('   Cleared store data')
            if part is None or part >= 1:
                District.objects.all().delete()
                self.stdout.write('   Cleared district data')
            self.stdout.write(self.style.SUCCESS('✅ Existing data cleared'))

        if part == 1:
            self.stdout.write('🏛️  PART 1: Seeding districts...')
            call_command('seed_districts', '--clear' if clear else '')
            districts_count = District.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✅ Part 1 complete: {districts_count} districts'))
            
        elif part == 2:
            self.stdout.write('🏪 PART 2: Seeding stores...')
            call_command('seed_stores', f'--stores-file={stores_file}', '--clear' if clear else '')
            stores_count = Store.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✅ Part 2 complete: {stores_count} stores'))
            
        elif part == 3:
            self.stdout.write('📦 PART 3: Seeding product catalog...')
            call_command('seed_products', '--clear' if clear else '')
            items_count = Item.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✅ Part 3 complete: {items_count} products'))
            
        elif part == 4:
            self.stdout.write('📋 PART 4: Seeding inventory...')
            call_command('seed_inventory', '--clear' if clear else '')
            inventory_count = Inventory.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✅ Part 4 complete: {inventory_count} inventory entries'))
            
        else:
            # Run all parts
            self.stdout.write('🚀 Seeding all Ho Chi Minh City data...')
            
            # Part 1: Districts
            self.stdout.write('🏛️  PART 1: Creating districts...')
            call_command('seed_districts')
            districts_count = District.objects.count()
            self.stdout.write(f'✅ Created {districts_count} districts')
            
            # Part 2: Stores 
            self.stdout.write('🏪 PART 2: Creating stores...')
            call_command('seed_stores', f'--stores-file={stores_file}')
            stores_count = Store.objects.count()
            self.stdout.write(f'✅ Created {stores_count} stores')
            
            # Part 3: Product catalog
            self.stdout.write('📦 PART 3: Creating product catalog...')
            call_command('seed_products')
            items_count = Item.objects.count()
            self.stdout.write(f'✅ Created {items_count} products')
            
            # Part 4: Inventory
            self.stdout.write('📋 PART 4: Creating inventory...')
            call_command('seed_inventory')
            inventory_count = Inventory.objects.count()
            self.stdout.write(f'✅ Created {inventory_count} inventory entries')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Successfully seeded all data: {districts_count} districts, '
                    f'{stores_count} stores, {items_count} products, {inventory_count} inventory entries'
                )
            ) 