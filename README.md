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
- **Environment Management**: Pixi for Python dependencies

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 16+
- Pixi (for Python environment management)

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

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Set up Python environment with Pixi:
   ```bash
   pixi install
   ```

3. Activate the Pixi environment:
   ```bash
   pixi shell
   ```

4. Install Python dependencies (if not using Pixi):
   ```bash
   pip install -r requirements.txt
   ```

5. Run Django migrations:
   ```bash
   python manage.py migrate
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
│   ├── pixi.toml           # Pixi environment configuration
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
├── docker-compose.yml      # Docker services configuration
└── README.md               # Project documentation
```

## Development

- Backend API runs on: http://localhost:8000
- Frontend runs on: http://localhost:3000
- Database runs on: localhost:5432
- Redis runs on: localhost:6379

## Testing

- Backend tests: `cd backend && python manage.py test`
- Frontend tests: `cd frontend && npm test`
- All tests: `npm run test:all`

## Environment Management

This project uses Pixi for Python environment management, which provides:
- Reproducible Python environments
- Automatic dependency resolution
- Cross-platform compatibility
- Better performance than traditional virtual environments

### Pixi Commands

```bash
# Install dependencies
pixi install

# Activate environment
pixi shell

# Add new dependency
pixi add package-name

# Remove dependency
pixi remove package-name

# Update dependencies
pixi update
```

## License

This project is created for educational purposes as part of a GIS Database course. 