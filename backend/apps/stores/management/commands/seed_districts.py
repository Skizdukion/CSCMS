"""
Django management command to seed districts with Ho Chi Minh City data.
Part 1: Districts with real GeoJSON boundaries.

Usage: python manage.py seed_districts
"""

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from decimal import Decimal
import json

from backend.apps.stores.models import District
from .seed_utils import get_geojson_path


class Command(BaseCommand):
    help = 'Seed the database with Ho Chi Minh City districts data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing districts before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing districts...')
            District.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing districts cleared'))

        self.stdout.write('🏛️  Seeding Ho Chi Minh City districts with real boundaries...')
        districts = self.seed_districts()
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully seeded {len(districts)} districts')
        )

    def seed_districts(self):
        """Create all Ho Chi Minh City districts with real boundaries from GeoJSON data."""
        geojson_path = get_geojson_path()
        
        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'GeoJSON file not found: {geojson_path}'))
            self.stdout.write(self.style.WARNING('Using fallback simple district data...'))
            return self._create_fallback_districts()
        
        # District type mapping based on Vietnamese names
        district_types = {
            'QUẬN': 'urban',
            'THÀNH PHỐ': 'suburban', 
            'HUYỆN': 'rural'
        }
        
        # Real population data (from official statistics)
        population_data = {
            'QUẬN 1': 204899,
            'QUẬN 3': 188945,
            'QUẬN 4': 180357,
            'QUẬN 5': 320149,
            'QUẬN 6': 253474,
            'QUẬN 7': 360155,
            'QUẬN 8': 489595,
            'QUẬN 10': 221498,
            'QUẬN 11': 266798,
            'QUẬN 12': 570502,
            'QUẬN GÒ VẤP': 647986,
            'QUẬN PHÚ NHUẬN': 163961,
            'QUẬN TÂN BÌNH': 430436,
            'QUẬN TÂN PHÚ': 442100,
            'QUẬN BÌNH THẠNH': 499164,
            'QUẬN BÌNH TÂN': 720000,
            'THÀNH PHỐ THỦ ĐỨC': 1200000,
            'HUYỆN HÓC MÔN': 435000,
            'HUYỆN CỦ CHI': 450000,
            'HUYỆN BÌNH CHÁNH': 725000,
            'HUYỆN NHÀ BÈ': 85000,
            'HUYỆN CẦN GIỜ': 75000,
        }
        
        # Real area data (square kilometers)
        area_data = {
            'QUẬN 1': 7.73,
            'QUẬN 3': 4.92,
            'QUẬN 4': 4.18,
            'QUẬN 5': 4.27,
            'QUẬN 6': 5.14,
            'QUẬN 7': 35.69,
            'QUẬN 8': 19.02,
            'QUẬN 10': 5.71,
            'QUẬN 11': 5.14,
            'QUẬN 12': 52.80,
            'QUẬN GÒ VẤP': 19.99,
            'QUẬN PHÚ NHUẬN': 4.88,
            'QUẬN TÂN BÌNH': 22.38,
            'QUẬN TÂN PHÚ': 16.06,
            'QUẬN BÌNH THẠNH': 20.76,
            'QUẬN BÌNH TÂN': 52.04,
            'THÀNH PHỐ THỦ ĐỨC': 211.53,
            'HUYỆN HÓC MÔN': 109.37,
            'HUYỆN CỦ CHI': 434.34,
            'HUYỆN BÌNH CHÁNH': 252.72,
            'HUYỆN NHÀ BÈ': 100.43,
            'HUYỆN CẦN GIỜ': 704.26,
        }
        
        # Average income data (VND per month, based on economic conditions)
        income_data = {
            'QUẬN 1': 75000000,      # Highest income (central business district)
            'QUẬN 3': 65000000,      # Historic, well-developed
            'QUẬN 4': 45000000,      # Dense urban area
            'QUẬN 5': 55000000,      # Chinatown, commercial
            'QUẬN 6': 48000000,      # Mixed residential/industrial
            'QUẬN 7': 70000000,      # Modern high-end residential
            'QUẬN 8': 42000000,      # Mixed residential/industrial
            'QUẬN 10': 50000000,     # Dense residential
            'QUẬN 11': 48000000,     # Residential
            'QUẬN 12': 38000000,     # Northwestern suburbs
            'QUẬN GÒ VẤP': 45000000, # Dense residential
            'QUẬN PHÚ NHUẬN': 65000000, # Central residential, high-end
            'QUẬN TÂN BÌNH': 52000000,  # Airport area, mixed
            'QUẬN TÂN PHÚ': 42000000,   # Western residential
            'QUẬN BÌNH THẠNH': 58000000, # Mixed development, growing
            'QUẬN BÌNH TÂN': 35000000,   # Newer residential area
            'THÀNH PHỐ THỦ ĐỨC': 60000000, # Tech hub, universities
            'HUYỆN HÓC MÔN': 32000000,      # Rural/suburban
            'HUYỆN CỦ CHI': 30000000,       # Rural, tourism
            'HUYỆN BÌNH CHÁNH': 35000000,   # Suburban development
            'HUYỆN NHÀ BÈ': 40000000,       # Industrial port area
            'HUYỆN CẦN GIỜ': 28000000,      # Remote rural/coastal
        }
        
        # District code mapping
        code_mapping = {
            'QUẬN 1': 'D1',
            'QUẬN 3': 'D3',
            'QUẬN 4': 'D4',
            'QUẬN 5': 'D5',
            'QUẬN 6': 'D6',
            'QUẬN 7': 'D7',
            'QUẬN 8': 'D8',
            'QUẬN 10': 'D10',
            'QUẬN 11': 'D11',
            'QUẬN 12': 'D12',
            'QUẬN GÒ VẤP': 'GV',
            'QUẬN PHÚ NHUẬN': 'PN',
            'QUẬN TÂN BÌNH': 'TB',
            'QUẬN TÂN PHÚ': 'TP',
            'QUẬN BÌNH THẠNH': 'BT',
            'QUẬN BÌNH TÂN': 'BTN',
            'THÀNH PHỐ THỦ ĐỨC': 'TDC',
            'HUYỆN HÓC MÔN': 'HM',
            'HUYỆN CỦ CHI': 'CC',
            'HUYỆN BÌNH CHÁNH': 'BC',
            'HUYỆN NHÀ BÈ': 'NB',
            'HUYỆN CẦN GIỜ': 'CG',
        }
        
        districts_data = []
        
        for feature in geojson_data['features']:
            vietnamese_name = feature['properties']['name']
            
            # Convert Vietnamese name to English name
            english_name = vietnamese_name.replace('QUẬN ', 'District ').replace('THÀNH PHỐ ', '').replace('HUYỆN ', '')
            
            # Determine district type
            district_type = 'urban'  # default
            for prefix, dtype in district_types.items():
                if vietnamese_name.startswith(prefix):
                    district_type = dtype
                    break
            
            # Get district code
            code = code_mapping.get(vietnamese_name, f'D{feature["properties"]["gid"]}')
            
            # Extract real polygon/multipolygon coordinates from GeoJSON
            try:
                geometry = feature['geometry']
                
                # Handle different geometry types from GeoJSON
                if geometry['type'] == 'MultiPolygon':
                    polygons = []
                    for polygon_coords in geometry['coordinates']:
                        # Each polygon_coords is [exterior_ring, hole1, hole2, ...]
                        exterior_ring = polygon_coords[0]
                        
                        # Simplify coordinates (take every nth point, max 50 points)
                        step = max(1, len(exterior_ring) // 50)
                        simplified_ring = exterior_ring[::step]
                        
                        # Ensure polygon is closed
                        if simplified_ring[0] != simplified_ring[-1]:
                            simplified_ring.append(simplified_ring[0])
                        
                        # Create polygon (GeoJSON is [lng, lat], Django expects [lng, lat])
                        if len(simplified_ring) >= 4:  # Minimum for valid polygon
                            polygon = Polygon(simplified_ring)
                            polygons.append(polygon)
                    
                    if polygons:
                        boundary = MultiPolygon(*polygons)
                    else:
                        raise ValueError("No valid polygons found")
                        
                elif geometry['type'] == 'Polygon':
                    # Single polygon
                    exterior_ring = geometry['coordinates'][0]
                    
                    # Simplify coordinates
                    step = max(1, len(exterior_ring) // 50)
                    simplified_ring = exterior_ring[::step]
                    
                    # Ensure polygon is closed
                    if simplified_ring[0] != simplified_ring[-1]:
                        simplified_ring.append(simplified_ring[0])
                    
                    if len(simplified_ring) >= 4:
                        polygon = Polygon(simplified_ring)
                        boundary = MultiPolygon(polygon)  # Convert to MultiPolygon for consistency
                    else:
                        raise ValueError("Invalid polygon coordinates")
                        
                elif geometry['type'] == 'GeometryCollection':
                    # Handle geometry collections
                    polygons = []
                    for geom in geometry['geometries']:
                        if geom['type'] == 'Polygon':
                            exterior_ring = geom['coordinates'][0]
                            step = max(1, len(exterior_ring) // 50)
                            simplified_ring = exterior_ring[::step]
                            if simplified_ring[0] != simplified_ring[-1]:
                                simplified_ring.append(simplified_ring[0])
                            if len(simplified_ring) >= 4:
                                polygon = Polygon(simplified_ring)
                                polygons.append(polygon)
                        elif geom['type'] == 'MultiPolygon':
                            # Handle MultiPolygon inside GeometryCollection
                            for polygon_coords in geom['coordinates']:
                                exterior_ring = polygon_coords[0]
                                step = max(1, len(exterior_ring) // 50)
                                simplified_ring = exterior_ring[::step]
                                if simplified_ring[0] != simplified_ring[-1]:
                                    simplified_ring.append(simplified_ring[0])
                                if len(simplified_ring) >= 4:
                                    polygon = Polygon(simplified_ring)
                                    polygons.append(polygon)
                    
                    if polygons:
                        boundary = MultiPolygon(*polygons)
                    else:
                        raise ValueError("No valid polygons in collection")
                else:
                    raise ValueError(f"Unsupported geometry type: {geometry['type']}")
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error processing geometry for {vietnamese_name}: {e}'))
                # Create a simple bounding box as fallback
                center_lat, center_lng = 10.8, 106.7  # Approximate center of HCM
                offset = 0.1
                boundary = MultiPolygon(
                    Polygon([
                        [center_lng - offset, center_lat - offset],
                        [center_lng + offset, center_lat - offset], 
                        [center_lng + offset, center_lat + offset],
                        [center_lng - offset, center_lat + offset],
                        [center_lng - offset, center_lat - offset]
                    ])
                )
            
            district_data = {
                'name': english_name,
                'code': code,
                'district_type': district_type,
                'population': population_data.get(vietnamese_name, 100000),
                'area_km2': Decimal(str(area_data.get(vietnamese_name, 10.0))),
                'avg_income': Decimal(str(income_data.get(vietnamese_name, 40000000))),
                'boundary': boundary
            }
            
            districts_data.append(district_data)
            
        # Create District objects
        districts = []
        for district_data in districts_data:
            district, created = District.objects.get_or_create(
                name=district_data['name'],
                defaults=district_data
            )
            districts.append(district)
            
            if created:
                self.stdout.write(f'Created district: {district.name} ({district.code})')
            else:
                self.stdout.write(f'District already exists: {district.name}')

        return districts

    def _create_fallback_districts(self):
        """Create simple fallback districts if GeoJSON file is not available."""
        self.stdout.write(self.style.WARNING('Creating fallback districts with simple boundaries...'))
        
        fallback_districts = [
            {
                'name': 'District 1',
                'code': 'D1',
                'district_type': 'urban',
                'population': 204899,
                'area_km2': Decimal('7.73'),
                'avg_income': Decimal('75000000'),
                'boundary': MultiPolygon(
                    Polygon([
                        [106.69, 10.76],
                        [106.71, 10.76],
                        [106.71, 10.78],
                        [106.69, 10.78],
                        [106.69, 10.76]
                    ])
                )
            },
            {
                'name': 'District 3',
                'code': 'D3',
                'district_type': 'urban',
                'population': 188945,
                'area_km2': Decimal('4.92'),
                'avg_income': Decimal('65000000'),
                'boundary': MultiPolygon(
                    Polygon([
                        [106.68, 10.78],
                        [106.70, 10.78],
                        [106.70, 10.80],
                        [106.68, 10.80],
                        [106.68, 10.78]
                    ])
                )
            }
        ]
        
        districts = []
        for district_data in fallback_districts:
            district, created = District.objects.get_or_create(
                name=district_data['name'],
                defaults=district_data
            )
            districts.append(district)
            
            if created:
                self.stdout.write(f'Created fallback district: {district.name}')
        
        return districts 