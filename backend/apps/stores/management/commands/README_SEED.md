# Seed Data Commands

The seed data system has been modularized into separate commands for better maintainability and flexibility.

## Overview

- `seed_data.py` - Main coordinator command that runs all parts
- `seed_districts.py` - Part 1: Districts with real GeoJSON boundaries
- `seed_stores.py` - Part 2: Stores from JSON file with coordinates
- `seed_products.py` - Part 3: Product catalog (predefined or random)
- `seed_inventory.py` - Part 4: Inventory relationships between stores and products
- `seed_utils.py` - Shared utilities for all seed commands

## Usage

### Run All Parts (Recommended)
```bash
python manage.py seed_data
python manage.py seed_data --clear  # Clear existing data first
```

### Run Individual Parts
```bash
# Part 1: Districts
python manage.py seed_districts
python manage.py seed_districts --clear

# Part 2: Stores (requires districts to exist)
python manage.py seed_stores
python manage.py seed_stores --stores-file=my_stores.json

# Part 3: Products
python manage.py seed_products
python manage.py seed_products --count=100  # Generate 100 random products

# Part 4: Inventory (requires stores and products to exist)
python manage.py seed_inventory
python manage.py seed_inventory --min-items=10 --max-items=25
```

### Run Specific Parts Only
```bash
python manage.py seed_data --part 1  # Districts only
python manage.py seed_data --part 2  # Stores only
python manage.py seed_data --part 3  # Products only
python manage.py seed_data --part 4  # Inventory only
```

## Part Details

### Part 1: Districts (`seed_districts`)
- **Purpose**: Create Ho Chi Minh City districts with real GeoJSON boundaries
- **Requirements**: `hcm_districts.geojson` file in commands directory
- **Features**:
  - Real boundary data from GeoJSON
  - Population, area, and income statistics
  - Fallback to simple boundaries if GeoJSON missing

### Part 2: Stores (`seed_stores`)
- **Purpose**: Create stores from JSON file with coordinates
- **Requirements**: Districts must exist (run Part 1 first)
- **JSON Format**:
```json
[
  {
    "name": "FamilyMart Nguyen Hue",
    "longitude": 106.7020,
    "latitude": 10.7770,
    "type": "convenience",
    "phone": "+84-28-123-4567",
    "opening_hours": "06:00-23:00",
    "rating": 4.5
  }
]
```
- **Features**:
  - Auto-detects district from coordinates
  - Generates realistic addresses
  - Creates sample file if JSON missing
  - Supports both `longitude/latitude` and `lng/lat` fields

### Part 3: Products (`seed_products`)
- **Purpose**: Create product catalog for convenience stores
- **Features**:
  - 50+ predefined realistic products
  - Option to generate random products
  - Categories: beverages, snacks, household, personal_care, other
  - Vietnamese brands and products

### Part 4: Inventory (`seed_inventory`)
- **Purpose**: Create inventory relationships between stores and products
- **Requirements**: Both stores and products must exist
- **Features**:
  - Random item selection per store
  - Configurable availability rates
  - Store type bias (supermarkets have more items)
  - Category bias (convenience stores prefer certain categories)

## File Structure

```
backend/apps/stores/management/commands/
├── seed_data.py          # Main coordinator
├── seed_districts.py     # Part 1: Districts
├── seed_stores.py        # Part 2: Stores
├── seed_products.py      # Part 3: Products
├── seed_inventory.py     # Part 4: Inventory
├── seed_utils.py         # Shared utilities
├── hcm_districts.geojson # GeoJSON boundaries
└── stores.json           # Your store data (create this)
```

## Configuration Files

### stores.json
Create this file with your store data:
```json
[
  {
    "name": "Store Name",
    "longitude": 106.7020,
    "latitude": 10.7770,
    "type": "convenience",          // optional
    "phone": "+84-28-123-4567",     // optional
    "email": "store@example.com",   // optional
    "opening_hours": "06:00-23:00", // optional
    "rating": 4.5,                  // optional
    "is_active": true               // optional
  }
]
```

Required fields: `name`, `longitude`, `latitude`

## Dependencies

- Districts must exist before creating stores
- Stores must exist before creating inventory
- Products must exist before creating inventory

## Examples

### Quick Start
```bash
# Create sample stores.json and run all parts
python manage.py seed_data

# Run with existing data cleared
python manage.py seed_data --clear
```

### Development Workflow
```bash
# 1. Set up districts
python manage.py seed_districts

# 2. Create your stores.json file, then:
python manage.py seed_stores --stores-file=stores.json

# 3. Add products
python manage.py seed_products

# 4. Generate inventory
python manage.py seed_inventory --min-items=20 --max-items=40
```

### Testing Different Scenarios
```bash
# Test with random products
python manage.py seed_products --count=200 --clear

# Test with high availability
python manage.py seed_inventory --availability-rate=0.9 --clear

# Test with store type bias
python manage.py seed_inventory --store-type-bias --category-bias --clear
``` 