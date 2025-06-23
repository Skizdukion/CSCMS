#!/bin/bash

# Convenience Store Management System - Backend Environment Activation Script
# This script activates the conda environment and sets up necessary environment variables

echo "🚀 Activating CSCMS Backend Environment..."

# Activate conda environment
conda activate cscms-backend

# Set Python path to include project root
export PYTHONPATH="/home/long/CSCMS:$PYTHONPATH"

# Set Django settings module
export DJANGO_SETTINGS_MODULE="backend.settings"

# Set environment variables for development
export DEBUG=True
export DJANGO_ENV=development

echo "✅ Environment activated successfully!"
echo "📁 Project root: /home/long/CSCMS"
echo "🐍 Python environment: cscms-backend"
echo "🔧 Django settings: backend.settings"
echo ""
echo "Available commands:"
echo "  python backend/manage.py runserver    # Start Django development server"
echo "  python backend/manage.py check        # Check Django configuration"
echo "  python backend/test_django_config.py  # Test GeoDjango setup"
echo "  docker-compose up -d db              # Start PostgreSQL with PostGIS"
echo ""
echo "To deactivate: conda deactivate" 