# Convenience Store Chain Management System

A web-based GIS-enabled management system for convenience stores across Ho Chi Minh City, Vietnam.

## Features

- **Spatial Data Management**: Store locations with geographic coordinates
- **CRUD Operations**: Add, search, edit, delete stores and inventory
- **Location-Based Analytics**: Statistics and reports by geographic regions
- **Interactive Maps**: Visualize stores and perform spatial analysis
- **Real-time Reporting**: Export data in multiple formats

## Technology Stack

- **Backend**: Django with GeoDjango (Python)
- **Frontend**: React.js with Leaflet.js for maps
- **Database**: PostgreSQL with PostGIS extension
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose
- **Environment Management**: Conda for Python dependencies

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Conda (Miniconda or Anaconda)
- Python 3.9+
- Node.js 16+

### Database Setup

1. Start the PostgreSQL database with PostGIS:
   ```bash
   docker-compose up -d db
   ```

2. Verify the database is running:
   ```bash
   docker-compose ps
   ```

3. Connect to the database to verify PostGIS is enabled:
   ```bash
   docker exec -it convenience_store_db psql -U postgres -d convenience_store_db -c "SELECT PostGIS_Version();"
   ```

### Backend Environment Setup

1. **Create and activate conda environment:**
   ```bash
   # Create conda environment with Python 3.11
   conda create -n cscms-backend python=3.11 -y
   
   # Activate the environment
   conda activate cscms-backend
   ```

2. **Install spatial dependencies (GDAL, GEOS, PROJ):**
   ```bash
   conda install -c conda-forge gdal geos proj -y
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Verify installation:**
   ```bash
   # Check Django and DRF
   python -c "import django; print('Django:', django.get_version())"
   python -c "import rest_framework; print('DRF:', rest_framework.VERSION)"
   
   # Check spatial libraries
   python -c "from osgeo import gdal; print('GDAL:', gdal.__version__)"
   
   # Check database connectivity
   python -c "import psycopg2; print('psycopg2:', psycopg2.__version__)"
   ```

### Backend Development

1. **Test Django configuration:**
   ```bash
   # From project root with PYTHONPATH set
   PYTHONPATH=$(pwd) python backend/manage.py check
   
   # Or use the test script
   PYTHONPATH=$(pwd) python backend/test_django_config.py
   ```

2. **Create and run migrations:**
   ```bash
   PYTHONPATH=$(pwd) python backend/manage.py makemigrations
   PYTHONPATH=$(pwd) python backend/manage.py migrate
   ```

3. **Run Django development server:**
   ```bash
   PYTHONPATH=$(pwd) python backend/manage.py runserver
   ```

### Seed Data

The system includes a comprehensive modular seed data system to populate the database with realistic Vietnamese convenience store data.

#### Seed Data Architecture

The seed system is split into 4 modular parts for easier maintenance and flexibility:

1. **Part 1: Districts** - Real Ho Chi Minh City districts with GeoJSON boundaries
2. **Part 2: Stores** - Store data from JSON file with auto-district detection
3. **Part 3: Products** - Vietnamese convenience store product catalog
4. **Part 4: Inventory** - Random inventory relationships between stores and products

#### Quick Seed (All Data)

To seed all data at once:
```bash
# Seed everything with sample data
PYTHONPATH=$(pwd) python backend/manage.py seed_data

# Clear existing data and seed everything
PYTHONPATH=$(pwd) python backend/manage.py seed_data --clear
```

#### Modular Seeding (Individual Parts)

**Part 1: Seed Districts**
```bash
# Clear existing districts and re-seed
PYTHONPATH=$(pwd) python backend/manage.py seed_districts --clear
```

**Part 2: Seed Stores**
```bash

# Clear existing stores and re-seed
PYTHONPATH=$(pwd) python backend/manage.py seed_stores --clear
```

**Part 3: Seed Products**
```bash
# Clear existing products and re-seed
PYTHONPATH=$(pwd) python backend/manage.py seed_products --clear
```

**Part 4: Seed Inventory**
```bash
# Clear existing inventory and re-seed
PYTHONPATH=$(pwd) python backend/manage.py seed_inventory --clear
```

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

## Development

- Backend API runs on: http://localhost:8000
- Frontend runs on: http://localhost:3000
- Database runs on: localhost:5432
- Redis runs on: localhost:6379

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/convenience_store_db
DATABASE_HOST=localhost
DATABASE_NAME=convenience_store_db
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Frontend Configuration
REACT_APP_API_URL=https://yourdomain.com/api
```

## Testing

### Prerequisites for Testing

Before running tests, ensure:
1. PostgreSQL database with PostGIS is running: `docker-compose up -d db`
2. Backend conda environment is activated: `conda activate cscms-backend`
3. All dependencies are installed: `pip install -r backend/requirements.txt`

### Backend Test Suite

The backend includes comprehensive test coverage with 119+ tests across different categories:

#### Running All Tests

**Using the test runner script (Recommended)**
```bash
conda activate cscms-backend && PYTHONPATH=$(pwd) python backend/test_runner.py
```

#### Running Specific Test Categories

**1. Model Tests (Database models, spatial fields, validation)**
```bash
cd backend
conda activate cscms-backend
export PYTHONPATH=/home/$USER/CSCMS:$PYTHONPATH
python manage.py test tests.stores.tests --settings=test_settings
```

## License

This project is created for educational purposes as part of a GIS Database course. 