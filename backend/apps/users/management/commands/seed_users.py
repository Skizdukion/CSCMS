from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    """
    Django management command to seed the database with predefined user accounts.
    Creates users for all roles: Administrator, Brand Manager, Store Manager, and Guest.
    """
    
    help = 'Seed the database with predefined user accounts for all roles'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing users',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Starting user seeding process...')
        )
        
        # Define predefined users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@cscms.com',
                'password': 'admin123456',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': User.Role.ADMINISTRATOR,
                'phone_number': '+84123456789',
                'address': 'Ho Chi Minh City, Vietnam',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'brand_manager',
                'email': 'brand.manager@cscms.com',
                'password': 'brand123456',
                'first_name': 'Brand',
                'last_name': 'Manager',
                'role': User.Role.BRAND_MANAGER,
                'phone_number': '+84987654321',
                'address': 'District 1, Ho Chi Minh City, Vietnam',
                'is_staff': True,
            },
            {
                'username': 'store_manager',
                'email': 'store.manager@cscms.com',
                'password': 'store123456',
                'first_name': 'Store',
                'last_name': 'Manager',
                'role': User.Role.STORE_MANAGER,
                'phone_number': '+84111222333',
                'address': 'District 3, Ho Chi Minh City, Vietnam',
                'is_staff': True,
            },
            {
                'username': 'guest_user',
                'email': 'guest@cscms.com',
                'password': 'guest123456',
                'first_name': 'Guest',
                'last_name': 'User',
                'role': User.Role.GUEST,
                'phone_number': '+84444555666',
                'address': 'District 7, Ho Chi Minh City, Vietnam',
            },
            {
                'username': 'demo_admin',
                'email': 'demo.admin@cscms.com',
                'password': 'demo123456',
                'first_name': 'Demo',
                'last_name': 'Admin',
                'role': User.Role.ADMINISTRATOR,
                'phone_number': '+84777888999',
                'address': 'District 2, Ho Chi Minh City, Vietnam',
                'is_staff': True,
            },
            {
                'username': 'demo_brand',
                'email': 'demo.brand@cscms.com',
                'password': 'demo123456',
                'first_name': 'Demo',
                'last_name': 'Brand',
                'role': User.Role.BRAND_MANAGER,
                'phone_number': '+84666777888',
                'address': 'District 5, Ho Chi Minh City, Vietnam',
                'is_staff': True,
            },
            {
                'username': 'demo_store',
                'email': 'demo.store@cscms.com',
                'password': 'demo123456',
                'first_name': 'Demo',
                'last_name': 'Store',
                'role': User.Role.STORE_MANAGER,
                'phone_number': '+84555666777',
                'address': 'District 10, Ho Chi Minh City, Vietnam',
                'is_staff': True,
            },
            {
                'username': 'demo_guest',
                'email': 'demo.guest@cscms.com',
                'password': 'demo123456',
                'first_name': 'Demo',
                'last_name': 'Guest',
                'role': User.Role.GUEST,
                'phone_number': '+84444777888',
                'address': 'District 11, Ho Chi Minh City, Vietnam',
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for user_data in users_data:
                username = user_data['username']
                email = user_data['email']
                
                # Check if user already exists
                try:
                    user = User.objects.get(username=username)
                    
                    if force:
                        # Update existing user
                        for field, value in user_data.items():
                            if field == 'password':
                                user.set_password(value)
                            else:
                                setattr(user, field, value)
                        user.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Updated user: {username}')
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Skipped existing user: {username}')
                        )
                        continue
                        
                except User.DoesNotExist:
                    # Create new user
                    password = user_data.pop('password')
                    user = User(**user_data)
                    user.set_password(password)
                    user.save()
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created user: {username}')
                    )
        
        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('User seeding completed!')
        )
        self.stdout.write(f'Created: {created_count} users')
        self.stdout.write(f'Updated: {updated_count} users')
        self.stdout.write(f'Skipped: {skipped_count} users')
        self.stdout.write('='*50)
        
        # Print login credentials
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('-'*30)
        for user_data in users_data:
            username = user_data['username']
            password = user_data.get('password', 'N/A')
            role = user_data['role']
            self.stdout.write(f'{username} ({role}): {password}')
        
        self.stdout.write('\n' + self.style.SUCCESS('All users are ready for testing!'))
