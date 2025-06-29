# Task List: Convenience Store Chain Management System

## Relevant Files

- `docker-compose.yml` - Docker configuration for PostgreSQL with PostGIS and Redis
- `database/init/01-init-postgis.sql` - Database initialization script for PostGIS extension
- `README.md` - Project documentation and setup instructions
- `backend/requirements.txt` - Python dependencies including GeoDjango and spatial libraries
- `backend/settings.py` - Django settings with GeoDjango configuration for spatial database
- `backend/urls.py` - Main URL configuration for Django backend with API endpoints
- `backend/wsgi.py` - WSGI configuration for Django application
- `backend/asgi.py` - ASGI configuration for Django application
- `backend/manage.py` - Django management script for running Django commands
- `backend/__init__.py` - Backend package initialization file
- `backend/apps/stores/__init__.py` - Stores app package initialization file
- `backend/apps/stores/apps.py` - Django app configuration for the stores app
- `backend/apps/stores/urls.py` - URL configuration for the stores app API endpoints
- `backend/apps/stores/models.py` - Django models for Store and Inventory with PostGIS spatial fields
- `backend/apps/stores/models.py` - Unit tests for models
- `backend/apps/stores/views.py` - Django views for CRUD operations and spatial queries
- `backend/apps/stores/views.py` - Unit tests for views
- `backend/apps/stores/serializers.py` - Django REST framework serializers for API responses
- `backend/apps/stores/admin.py` - Django admin interface configuration
- `backend/apps/stores/utils/spatial_helpers.py` - Utility functions for spatial calculations
- `backend/apps/stores/utils/spatial_helpers.py` - Unit tests for spatial utilities
- `backend/apps/stores/migrations/` - Django database migrations for spatial data models
- `backend/apps/stores/migrations/0003_remove_inventory_fields.py` - Migration to remove quantity, price, and min_stock_level fields from inventory
- `backend/core/__init__.py` - Core backend utilities package
- `backend/core/middleware.py` - Custom middleware for the application
- `backend/core/permissions.py` - Custom permissions for API access
- `backend/core/exceptions.py` - Custom exception handlers
- `backend/api/__init__.py` - API package initialization
- `backend/api/urls.py` - Main API URL routing
- `backend/api/views.py` - API-level views and endpoints
- `backend/utils/__init__.py` - Backend utilities package
- `backend/utils/spatial_helpers.py` - Global spatial utility functions
- `backend/utils/spatial_helpers.py` - Unit tests for spatial utilities
- `backend/utils/validators.py` - Custom validators for spatial data
- `backend/utils/validators.py` - Unit tests for validators
- `test_django_config.py` - Test script to verify Django configuration and GeoDjango setup
- `frontend/package.json` - Node.js dependencies including React and routing libraries
- `frontend/src/App.tsx` - Main React application with routing setup
- `frontend/src/components/Layout/Layout.tsx` - Main layout component with sidebar navigation
- `frontend/src/components/Layout/Layout.css` - Styles for the layout component
- `frontend/src/pages/Dashboard.tsx` - Dashboard page with live API data, overview cards, quick actions, and integrated map modal with store markers
- `frontend/src/pages/Dashboard.css` - Styles for the dashboard page including modal, loading states, and map legend
- `frontend/src/pages/Stores.tsx` - Stores management page with store cards and filters
- `frontend/src/pages/Stores.css` - Styles for the stores page
- `frontend/src/pages/Inventory.tsx` - Inventory management page with table view
- `frontend/src/pages/Inventory.css` - Styles for the inventory page
- `frontend/src/pages/Reports.tsx` - Reports and analytics page with charts and metrics
- `frontend/src/pages/Reports.css` - Styles for the reports page
- `frontend/src/components/Map/StoreMap.jsx` - Interactive map component with Leaflet.js, multiple tile layers, enhanced store markers with visual status indicators, rich popup information, and advanced controls
- `frontend/src/components/Map/StoreMap.css` - CSS styles for the map component including enhanced popup styling, marker status indicators, and advanced control styling
- `frontend/src/components/Map/StoreMap.test.jsx` - Comprehensive unit tests for map component including enhanced popup functionality (17 test cases)
- `frontend/src/components/Store/StoreForm.tsx` - Form component for adding/editing stores
- `frontend/src/components/Store/StoreForm.css` - Styles for the store form component
- `frontend/src/types/index.ts` - TypeScript interfaces for Store, District, and form data
- `frontend/src/components/Store/StoreList.jsx` - Store listing and search component
- `frontend/src/components/Store/StoreList.jsx` - Unit tests for store list
- `frontend/src/components/Inventory/InventoryForm.jsx` - Inventory management form
- `frontend/src/components/Inventory/InventoryForm.jsx` - Unit tests for inventory form
- `frontend/src/components/Inventory/ItemEditForm.tsx` - Form component for editing item details (name and status only)
- `frontend/src/components/Inventory/ItemEditForm.css` - Styles for the item edit form component
- `frontend/src/components/Inventory/ItemStoreForm.tsx` - Form component for managing which stores have a specific item
- `frontend/src/components/Inventory/ItemStoreForm.css` - Styles for the item store management form
- `frontend/src/components/Reports/StatisticsReport.jsx` - Statistics and reporting component
- `frontend/src/components/Reports/StatisticsReport.jsx` - Unit tests for reports
- `frontend/src/services/api.ts` - API service functions for backend communication with TypeScript support
- `frontend/src/services/api.ts` - Unit tests for API services
- `frontend/src/utils/constants.js` - Application constants and configuration
- `backend/tests/stores/test_views.py` - API view tests for the stores app
- `backend/tests/stores/test_serializers.py` - Serializer tests for the stores app
- `backend/tests/stores/tests.py` - Model and integration tests for the stores app
- `backend/apps/stores/management/commands/seed_data.py` - Django management command for seeding HCM City data
- `backend/tests/stores/test_advanced_search.py` - Unit tests for advanced search functionality including location-based search and inventory filtering

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `MyComponent.tsx` and `MyComponent.test.tsx` in the same directory).
- Use `npx jest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the Jest configuration.
- Spatial data operations require PostGIS extension in PostgreSQL.
- Map components will use Leaflet.js for OpenStreetMap integration.
- Backend follows modular structure: `backend/apps/` for Django apps, `backend/core/` for core utilities, `backend/api/` for API-level code.
- Python dependencies are managed in `backend/requirements.txt`.
- Frontend uses React with TypeScript and React Router for navigation.

## Tasks

- [x] 1.0 Database Setup and Spatial Models
  - [x] 1.1 Set up PostgreSQL database with PostGIS extension
  - [x] 1.2 Create and check backend Python environment server using conda
    - [x] 1.2.1 Create conda environment with Python 3.9+ and required packages
    - [x] 1.2.2 Install GeoDjango and spatial dependencies (GDAL, GEOS, PROJ)
    - [x] 1.2.3 Install Django and Django REST framework
    - [x] 1.2.4 Install PostgreSQL adapter (psycopg2) and Redis client
    - [x] 1.2.5 Test Django server startup and basic configuration
    - [x] 1.2.6 Verify GeoDjango spatial database connectivity
    - [x] 1.2.7 Create environment activation script for development
    - [x] 1.2.8 Document environment setup process in README
  - [x] 1.3 Create Store model with spatial fields (PointField for coordinates)
  - [x] 1.4 Create Inventory model with store relationship
  - [x] 1.5 Create District model for geographic boundaries
  - [x] 1.6 Add spatial indexes to models for performance optimization
  - [x] 1.7 Create and run database migrations
  - [x] 1.8 Write unit tests for models and spatial field validation
  - [x] 1.9 Configure Django admin interface for spatial data management

- [x] 2.0 Backend API Development
  - [x] 2.1 Set up Django REST framework with spatial serializers
  - [x] 2.1.1 Reorganize all backend test files into backend/tests/ with subfolders for each app
  - [x] 2.2 Create StoreViewSet with CRUD operations
  - [x] 2.3 Implement spatial search endpoints (radius search, district search)
  - [x] 2.4 Create InventoryViewSet with store association
  - [x] 2.5 Add spatial utility functions for distance calculations
  - [x] 2.6 Implement store statistics endpoints (count by district, density analysis)
  - [x] 2.7 Add filtering and pagination to API endpoints
  - [x] 2.8 Create API documentation using DRF schema
  - [x] 2.9 Write comprehensive unit tests for all API endpoints
  - [x] 2.10 Add error handling and validation for spatial data
  - [x] 2.11 Seed data with Ho Chi Minh City convenience stores and districts
  - [x] 2.12 Comprehensive unit test with database test

- [x] 3.0 Frontend User Interface
  - [x] 3.1 Set up React application with routing and state management
  - [x] 3.2 Create main navigation and layout components
  - [x] 3.3 Complete store management page (with API communication)
    - [x] 3.3.1 Add new store and edit store feature (create and edit form, form validation, api submitting)
    - [x] 3.3.2 Search store feature (search by name, advanced option for filter district, available inventory, store type, is active, sort by near a picked location)
  - [ ] 3.4 Complete item management page (with API communication)
    - [x] 3.4.1 Search item (Categories filter, status filter)
    - [x] 3.4.2 Add new item, edit item, delete item feature (create and edit form, form validation)
    - [x] 3.4.3 Remove quantity, price, and minimum stock level fields from backend and frontend
    - [x] 3.4.4 Create ItemEditForm component for editing item name and status only
    - [x] 3.4.5 Create ItemStoreForm component for managing which stores have an item

- [ ] 4.0 Map Integration and Spatial Features
  - [x] 4.1 Set up Leaflet.js map component with OpenStreetMap tiles
  - [x] 4.2 Add map controls for zoom, pan, and layer toggling
  - [x] 4.3 Implement store markers with popup information from api (using in dashboard view map button)
  - [x] 4.4 Using picking location in Add or Edit store form (location details, allow pick location -> auto extract long and lat, or mannualy set long and lat by number, not allow to select district, this need to be auto mapping from location)

- [x] 5.0 Final touch
  - [x] 5.1 Fix search box to be strech horizontal
  - [x] 5.2 Allow to view all inventory in a store by Inventory button in store card
  - [x] 5.3 Remove inventory summary and reports & analytic page & main header

- [ ] 6.0 E2E test case with Playwright