"""
Django management command to seed inventory relationships.
Part 4: Inventory relationships between stores and products with random availability.

Usage: python manage.py seed_inventory
"""

from django.core.management.base import BaseCommand
import random

from backend.apps.stores.models import Store, Item, Inventory


class Command(BaseCommand):
    help = 'Seed the database with inventory relationships between stores and products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing inventory before seeding',
        )
        parser.add_argument(
            '--min-items',
            type=int,
            default=15,
            help='Minimum number of items per store (default: 15)',
        )
        parser.add_argument(
            '--max-items',
            type=int,
            default=35,
            help='Maximum number of items per store (default: 35)',
        )
        parser.add_argument(
            '--availability-rate',
            type=float,
            default=0.75,
            help='Probability that an item is available (0.0-1.0, default: 0.75)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing inventory...')
            Inventory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing inventory cleared'))

        # Check prerequisites
        stores = Store.objects.all()
        items = Item.objects.all()
        
        if not stores.exists():
            self.stdout.write(self.style.ERROR('No stores found. Please run: python manage.py seed_stores'))
            return
        
        if not items.exists():
            self.stdout.write(self.style.ERROR('No items found. Please run: python manage.py seed_products'))
            return

        min_items = options.get('min_items', 15)
        max_items = options.get('max_items', 35)
        availability_rate = options.get('availability_rate', 0.75)
        
        self.stdout.write(f'📋 Seeding inventory for {stores.count()} stores with {items.count()} products...')
        self.stdout.write(f'   Items per store: {min_items}-{max_items}')
        self.stdout.write(f'   Availability rate: {availability_rate*100:.0f}%')
        
        inventory_count = self.seed_inventory(stores, items, min_items, max_items, availability_rate)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully seeded {inventory_count} inventory relationships')
        )

    def seed_inventory(self, stores, items, min_items, max_items, availability_rate):
        """Create inventory relationships between stores and items."""
        inventory_count = 0
        items_list = list(items)
        
        for store in stores:
            # Determine how many items this store will have
            num_items = random.randint(min_items, min(max_items, len(items_list)))
            
            # Select random items for this store
            store_items = random.sample(items_list, num_items)
            
            self.stdout.write(f'Processing {store.name}: {len(store_items)} items')
            
            for item in store_items:
                # Determine availability
                is_available = random.random() < availability_rate
                
                inventory_data = {
                    'store': store,
                    'item': item,
                    'is_available': is_available
                }
                
                inventory, created = Inventory.objects.get_or_create(
                    store=store,
                    item=item,
                    defaults=inventory_data
                )
                
                if created:
                    inventory_count += 1
                    status = "✅ Available" if is_available else "❌ Unavailable"
                    self.stdout.write(f'  {item.name}: {status}')
                else:
                    self.stdout.write(f'  {item.name}: Already exists')
        
        return inventory_count

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--store-type-bias',
            action='store_true',
            help='Apply bias based on store type (larger stores have more items)',
        )
        parser.add_argument(
            '--category-bias',
            action='store_true',
            help='Apply category bias (convenience stores prefer certain categories)',
        )

    def seed_inventory_with_bias(self, stores, items, min_items, max_items, availability_rate, store_type_bias=False, category_bias=False):
        """Create inventory relationships with realistic bias based on store type and item categories."""
        inventory_count = 0
        items_list = list(items)
        
        # Store type item count multipliers
        store_type_multipliers = {
            'convenience': 1.0,
            'mini-mart': 1.3,
            'supermarket': 1.8,
        }
        
        # Category preference by store type
        category_preferences = {
            'convenience': {
                'beverages': 1.5,
                'snacks': 1.4,
                'personal_care': 1.2,
                'household': 0.8,
                'other': 1.0,
            },
            'mini-mart': {
                'beverages': 1.3,
                'snacks': 1.3,
                'personal_care': 1.1,
                'household': 1.2,
                'other': 1.0,
            },
            'supermarket': {
                'beverages': 1.2,
                'snacks': 1.2,
                'personal_care': 1.1,
                'household': 1.4,
                'other': 1.1,
            },
        }
        
        for store in stores:
            # Calculate item count based on store type
            base_items = random.randint(min_items, max_items)
            if store_type_bias:
                multiplier = store_type_multipliers.get(store.store_type, 1.0)
                num_items = min(int(base_items * multiplier), len(items_list))
            else:
                num_items = base_items
            
            # Select items with category bias if enabled
            if category_bias:
                store_items = self._select_items_with_bias(
                    items_list, 
                    num_items, 
                    category_preferences.get(store.store_type, {})
                )
            else:
                store_items = random.sample(items_list, num_items)
            
            self.stdout.write(f'Processing {store.name} ({store.store_type}): {len(store_items)} items')
            
            for item in store_items:
                # Availability rate can vary by category
                item_availability_rate = availability_rate
                if category_bias:
                    # High-demand categories might have slightly lower availability
                    if item.category in ['beverages', 'snacks']:
                        item_availability_rate *= 0.9
                    elif item.category in ['household']:
                        item_availability_rate *= 1.1
                
                is_available = random.random() < item_availability_rate
                
                inventory_data = {
                    'store': store,
                    'item': item,
                    'is_available': is_available
                }
                
                inventory, created = Inventory.objects.get_or_create(
                    store=store,
                    item=item,
                    defaults=inventory_data
                )
                
                if created:
                    inventory_count += 1
        
        return inventory_count
    
    def _select_items_with_bias(self, items_list, num_items, category_preferences):
        """Select items with category bias."""
        if not category_preferences:
            return random.sample(items_list, num_items)
        
        # Create weighted list based on category preferences
        weighted_items = []
        for item in items_list:
            weight = category_preferences.get(item.category, 1.0)
            # Add item multiple times based on weight
            weighted_items.extend([item] * int(weight * 10))
        
        # Select items (with possible duplicates, then remove duplicates)
        selected = []
        attempts = 0
        while len(selected) < num_items and attempts < num_items * 3:
            item = random.choice(weighted_items)
            if item not in selected:
                selected.append(item)
            attempts += 1
        
        # If we still don't have enough, fill with random items
        if len(selected) < num_items:
            remaining_items = [item for item in items_list if item not in selected]
            needed = num_items - len(selected)
            if remaining_items:
                selected.extend(random.sample(remaining_items, min(needed, len(remaining_items))))
        
        return selected[:num_items] 