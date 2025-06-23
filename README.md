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

### Using Environment Activation Scripts

For convenience, we provide activation scripts that set up the environment automatically:

**Linux/macOS:**
```bash
source scripts/activate_backend.sh
```

**Windows:**
```cmd
scripts\activate_backend.bat
```

These scripts will:
- Activate the conda environment
- Set the correct PYTHONPATH
- Configure Django settings
- Display available commands

### Backend Development

1. **Test Django configuration:**
   ```bash
   # From project root with PYTHONPATH set
   PYTHONPATH=$(pwd) python backend/manage.py check
   
   # Or use the test script
   PYTHONPATH=$(pwd) python backend/test_django_config.py
   ```

2. **Run Django development server:**
   ```bash
   PYTHONPATH=$(pwd) python backend/manage.py runserver
   ```

3. **Create and run migrations:**
   ```bash
   PYTHONPATH=$(pwd) python backend/manage.py makemigrations
   PYTHONPATH=$(pwd) python backend/manage.py migrate
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

## Project Structure

```
├── backend/                 # Django backend application
│   ├── requirements.txt    # Python dependencies
│   ├── manage.py           # Django management script
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   ├── asgi.py             # ASGI configuration
│   ├── apps/               # Django applications
│   │   └── stores/         # Stores app
│   │       ├── models.py   # Database models with spatial fields
│   │       ├── views.py    # API views and spatial queries
│   │       ├── serializers.py # DRF serializers
│   │       └── migrations/ # Database migrations
│   ├── api/                # API-level code
│   │   ├── urls.py         # Main API routing
│   │   └── views.py        # API-level views
│   ├── core/               # Core utilities
│   │   ├── middleware.py   # Custom middleware
│   │   ├── permissions.py  # Custom permissions
│   │   └── exceptions.py   # Custom exceptions
│   └── utils/              # Global utilities
│       ├── spatial_helpers.py # Spatial utility functions
│       └── validators.py   # Custom validators
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
├── database/               # Database initialization scripts
├── scripts/                # Environment activation scripts
│   ├── activate_backend.sh # Linux/macOS activation script
│   └── activate_backend.bat # Windows activation script
├── docker-compose.yml      # Docker services configuration
└── README.md               # Project documentation
```

## Development

- Backend API runs on: http://localhost:8000
- Frontend runs on: http://localhost:3000
- Database runs on: localhost:5432
- Redis runs on: localhost:6379

## Testing

- Backend tests: `cd backend && PYTHONPATH=$(pwd)/.. python manage.py test`
- Frontend tests: `cd frontend && npm test`
- Django configuration test: `PYTHONPATH=$(pwd) python backend/test_django_config.py`

## Environment Management

This project uses Conda for Python environment management, which provides:
- Reproducible Python environments
- Easy installation of spatial libraries (GDAL, GEOS, PROJ)
- Cross-platform compatibility
- Integration with pip for additional packages

### Conda Commands

```bash
# Create environment
conda create -n cscms-backend python=3.11 -y

# Activate environment
conda activate cscms-backend

# Install spatial dependencies
conda install -c conda-forge gdal geos proj -y

# Install Python packages via pip
pip install -r backend/requirements.txt

# Deactivate environment
conda deactivate

# List environments
conda env list

# Remove environment (if needed)
conda env remove -n cscms-backend
```

### Troubleshooting

**Common Issues:**

1. **"No module named 'backend'" error:**
   - Always set PYTHONPATH when running Django commands from project root
   - Use: `PYTHONPATH=$(pwd) python backend/manage.py [command]`

2. **GDAL import errors:**
   - Ensure GDAL is installed via conda: `conda install -c conda-forge gdal`
   - Use `from osgeo import gdal` instead of `import gdal`

3. **Database connection issues:**
   - Ensure PostgreSQL with PostGIS is running: `docker-compose up -d db`
   - Check database credentials in `backend/settings.py`

4. **Spatial library issues:**
   - Install from conda-forge channel: `conda install -c conda-forge gdal geos proj`
   - Verify installation: `python -c "from osgeo import gdal; print(gdal.__version__)"`

## License

This project is created for educational purposes as part of a GIS Database course. 