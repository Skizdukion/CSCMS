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

## Production Deployment

### Prerequisites for Production

- Docker and Docker Compose
- Python 3.9+ with conda environment
- Node.js 16+ for frontend builds
- PostgreSQL with PostGIS extension
- Redis server
- Web server (Nginx recommended)

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

### Backend Production Setup

1. **Activate conda environment and install production dependencies:**
   ```bash
   conda activate cscms-backend
   pip install gunicorn whitenoise
   ```

2. **Configure production settings:**
   ```bash
   # Create production settings file
   cp backend/settings.py backend/settings.py
   ```

3. **Run database migrations:**
   ```bash
   PYTHONPATH=$(pwd) python backend/manage.py migrate --settings=backend.settings
   ```

4. **Collect static files:**
   ```bash
   PYTHONPATH=$(pwd) python backend/manage.py collectstatic --noinput --settings=backend.settings
   ```

5. **Load initial data (if needed):**
   ```bash
   PYTHONPATH=$(pwd) python backend/manage.py seed_data --settings=backend.settings
   ```

6. **Start production server with Gunicorn:**
   ```bash
   # Single worker (for testing)
   PYTHONPATH=$(pwd) gunicorn --bind 0.0.0.0:8000 --chdir backend backend.wsgi:application

   # Multiple workers (recommended for production)
   PYTHONPATH=$(pwd) gunicorn --bind 0.0.0.0:8000 --workers 3 --worker-class gevent --worker-connections 1000 --chdir backend backend.wsgi:application

   # With process management (recommended)
   PYTHONPATH=$(pwd) gunicorn --bind 0.0.0.0:8000 --workers 3 --worker-class gevent --worker-connections 1000 --chdir backend --daemon --pid /var/run/gunicorn.pid --log-file /var/log/gunicorn.log backend.wsgi:application
   ```

### Frontend Production Setup

1. **Install dependencies and build:**
   ```bash
   cd frontend
   npm ci --production
   npm run build
   ```

2. **Serve with a web server (Nginx example):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       # Frontend static files
       location / {
           root /path/to/your/project/frontend/build;
           try_files $uri $uri/ /index.html;
       }
       
       # Backend API
       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       # Django admin
       location /admin/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### Docker Production Setup

1. **Start all services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Run migrations in production container:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
   docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
   ```

### Production Monitoring and Maintenance

1. **Check application logs:**
   ```bash
   # Gunicorn logs
   tail -f /var/log/gunicorn.log
   
   # Django application logs
   tail -f /var/log/django.log
   
   # Docker logs
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

2. **Database backup:**
   ```bash
   # Create backup
   docker exec convenience_store_db pg_dump -U postgres convenience_store_db > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # Restore backup
   docker exec -i convenience_store_db psql -U postgres convenience_store_db < backup.sql
   ```

3. **Health checks:**
   ```bash
   # Check backend API health
   curl https://yourdomain.com/api/stores/

   # Check database connection
   docker exec convenience_store_db psql -U postgres -d convenience_store_db -c "SELECT PostGIS_Version();"
   
   # Check Redis connection
   docker exec convenience_store_redis redis-cli ping
   ```

### Performance Optimization

1. **Enable Django caching:**
   ```python
   # In settings_prod.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://localhost:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```

2. **Optimize database queries:**
   ```bash
   # Enable query logging in development to identify slow queries
   PYTHONPATH=$(pwd) python backend/manage.py shell
   >>> from django.db import connection
   >>> print(connection.queries)
   ```

3. **Configure spatial indexes:**
   ```bash
   # Spatial indexes are automatically created by PostGIS for GeoDjango fields
   # Verify indexes exist:
   docker exec convenience_store_db psql -U postgres -d convenience_store_db -c "\d+ stores_store;"
   ```

### Security Considerations

1. **HTTPS Setup:** Always use HTTPS in production with SSL certificates
2. **CORS Configuration:** Configure CORS settings for your domain
3. **Database Security:** Use strong passwords and limit database access
4. **Environment Variables:** Never commit sensitive data to version control
5. **Static Files:** Serve static files through a CDN or web server, not Django
6. **Backup Strategy:** Implement regular automated backups
7. **Monitoring:** Set up application monitoring and error tracking

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