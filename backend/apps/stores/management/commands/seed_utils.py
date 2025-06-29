"""
Shared utilities for seed data commands.
"""

import random
import os
from django.contrib.gis.geos import Point
from backend.apps.stores.models import District


def detect_district_from_coordinates(longitude, latitude, stdout=None):
    """Detect district from coordinates using spatial query (like frontend does)."""
    try:
        point = Point(longitude, latitude, srid=4326)
        district = District.objects.filter(boundary__contains=point).first()
        if district:
            return district
        else:
            # Fallback: find nearest district
            if stdout:
                stdout.write(f'Point ({longitude}, {latitude}) not within any district boundary, using nearest')
            nearest_district = District.objects.filter(boundary__isnull=False).extra(
                select={'distance': 'ST_Distance(boundary, ST_GeomFromText(%s, 4326))'},
                select_params=[point.wkt],
                order_by=['distance']
            ).first()
            return nearest_district
    except Exception as e:
        if stdout:
            stdout.write(f'Error detecting district for ({longitude}, {latitude}): {e}')
        return District.objects.first()  # Fallback to first district


def generate_address_from_coordinates(longitude, latitude, district_name):
    """Generate a realistic address from coordinates and district name."""
    # Ho Chi Minh City street names
    street_names = [
        'Nguyen Hue', 'Le Loi', 'Dong Khoi', 'Pasteur', 'Vo Van Tan', 'Truong Dinh',
        'Nam Ky Khoi Nghia', 'Tran Hung Dao', 'Hai Ba Trung', 'Ly Tu Trong',
        'Nguyen Du', 'Mac Dinh Chi', 'Vo Thi Sau', 'Cach Mang Thang Tam',
        'Pham Ngu Lao', 'De Tham', 'Bui Vien', 'Nguyen Thai Hoc', 'Le Thanh Ton',
        'Dinh Tien Hoang', 'Nguyen Dinh Chieu', 'Cong Quynh', 'An Duong Vuong',
        'Lac Long Quan', 'Tran Phu', 'Phan Xich Long', 'Hoang Van Thu',
        'Le Van Sy', 'Nguyen Tat Thanh', 'Vo Van Kiet', 'Tran Quoc Toan',
        'Dien Bien Phu', 'Xo Viet Nghe Tinh', 'Nguyen Thi Minh Khai', 'Ba Huyen Thanh Quan'
    ]
    
    # Generate address based on coordinates (use them to seed random for consistency)
    random.seed(int((longitude + latitude) * 10000))
    street_name = random.choice(street_names)
    street_number = random.randint(1, 500)
    
    return f"{street_number} {street_name}, {district_name}, Ho Chi Minh City"


def get_geojson_path():
    """Get the path to the HCM districts GeoJSON file."""
    return os.path.join(os.path.dirname(__file__), 'hcm_districts.geojson')


def get_stores_json_path(filename='stores.json'):
    """Get the path to the stores JSON file."""
    return os.path.join(os.path.dirname(__file__), filename) 