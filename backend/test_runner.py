#!/usr/bin/env python
"""
Test runner for the convenience store management system.
This script runs all tests using SQLite with SpatiaLite for faster execution.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Set the Django settings module to use test settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.test_settings')
    
    # Setup Django
    django.setup()
    
    # Get the Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run tests
    failures = test_runner.run_tests([
        "backend.tests.stores.tests",
        "backend.tests.stores.test_serializers", 
        "backend.tests.stores.test_views",
        "backend.tests.stores.test_database_comprehensive",
        "backend.tests.stores.test_advanced_search"
    ])
    
    if failures:
        sys.exit(bool(failures)) 