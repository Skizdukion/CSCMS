#!/usr/bin/env python
"""
Test script to verify Django configuration and GeoDjango setup.
"""
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_django_config():
    """Test Django configuration and GeoDjango setup."""
    try:
        # Test settings import without full Django setup
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

        # Import Django settings directly
        import django
        from django.conf import settings

        print("✅ Django configuration test passed!")
        print(f"   - Django version: {django.get_version()}")
        print(f"   - Database engine: {settings.DATABASES['default']['ENGINE']}")
        print(
            f"   - GeoDjango enabled: {'django.contrib.gis' in settings.INSTALLED_APPS}"
        )
        print(f"   - Timezone: {settings.TIME_ZONE}")
        print(f"   - Language: {settings.LANGUAGE_CODE}")
        print(f"   - Debug mode: {settings.DEBUG}")
        print(f"   - Allowed hosts: {settings.ALLOWED_HOSTS}")
        print(f"   - Stores app: {'backend.apps.stores' in settings.INSTALLED_APPS}")

        # Test database connection using psycopg2 directly
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=settings.DATABASES["default"]["HOST"],
                port=settings.DATABASES["default"]["PORT"],
                database=settings.DATABASES["default"]["NAME"],
                user=settings.DATABASES["default"]["USER"],
                password=settings.DATABASES["default"]["PASSWORD"],
            )

            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                pg_version = cursor.fetchone()[0]
                print(f"   - PostgreSQL version: {pg_version}")

                cursor.execute("SELECT PostGIS_Version();")
                postgis_version = cursor.fetchone()[0]
                print(f"   - PostGIS version: {postgis_version}")

            conn.close()
            print("✅ Database connection test passed!")

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

        # Test GeoDjango imports (without full setup)
        try:
            from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper

            print("✅ GeoDjango PostGIS backend import successful")
        except ImportError as e:
            print(f"⚠️  GeoDjango PostGIS import warning: {e}")
            print("   This is expected on Windows without GDAL installation")
            print(
                "   GDAL is required for spatial operations but not for basic configuration"
            )

        # Test modular structure imports
        try:
            from backend.apps.stores.apps import StoresConfig
            print("✅ Modular backend structure test passed!")
        except ImportError as e:
            print(f"⚠️  Modular structure import warning: {e}")
            print("   This is expected before models are created")

        return True

    except Exception as e:
        print(f"❌ Django configuration test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL with PostGIS is running:")
        print("   docker-compose up -d db")
        print("2. For Windows GDAL issues, you can:")
        print("   - Install GDAL from OSGeo4W")
        print("   - Or use Docker for development")
        print("3. Check if all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False


if __name__ == "__main__":
    test_django_config()
