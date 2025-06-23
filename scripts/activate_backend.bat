@echo off
REM Convenience Store Management System - Backend Environment Activation Script (Windows)
REM This script activates the conda environment and sets up necessary environment variables

echo 🚀 Activating CSCMS Backend Environment...

REM Activate conda environment
call conda activate cscms-backend

REM Set Python path to include project root
set PYTHONPATH=C:\path\to\CSCMS;%PYTHONPATH%

REM Set Django settings module
set DJANGO_SETTINGS_MODULE=backend.settings

REM Set environment variables for development
set DEBUG=True
set DJANGO_ENV=development

echo ✅ Environment activated successfully!
echo 📁 Project root: C:\path\to\CSCMS
echo 🐍 Python environment: cscms-backend
echo 🔧 Django settings: backend.settings
echo.
echo Available commands:
echo   python backend\manage.py runserver    # Start Django development server
echo   python backend\manage.py check        # Check Django configuration
echo   python backend\test_django_config.py  # Test GeoDjango setup
echo   docker-compose up -d db              # Start PostgreSQL with PostGIS
echo.
echo To deactivate: conda deactivate 