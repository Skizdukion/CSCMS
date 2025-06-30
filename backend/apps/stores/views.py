"""
Django REST framework API views for the stores app with spatial querying support.
"""

from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Count, Avg, Q
from functools import reduce
import operator
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Store, Item, Inventory, District
from .serializers import StoreSerializer, ItemSerializer, InventorySerializer, DistrictSerializer, StoreListSerializer, InventoryListSerializer, SpatialSearchSerializer, DistrictSearchSerializer, StoreStatisticsSerializer, DistrictStatisticsSerializer, StoreLocationSerializer

class StoreViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing stores.
    
    Provides CRUD operations for Store model with spatial location support.
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store_type', 'city', 'district', 'is_active']
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['name', 'city', 'rating', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        return Store.objects.select_related('district_obj').prefetch_related('inventories')

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return StoreListSerializer
        return StoreSerializer





    @extend_schema(
        summary="Get store statistics",
        description="Get comprehensive statistics about stores",
        responses={200: StoreStatisticsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get store statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_stores': queryset.count(),
            'active_stores': queryset.filter(is_active=True).count(),
            'stores_by_type': dict(queryset.values_list('store_type').annotate(count=Count('id'))),
            'stores_by_district': dict(queryset.values_list('district_obj__name').annotate(count=Count('id'))),
            'average_rating': queryset.aggregate(avg=Avg('rating'))['avg'] or 0,
            'total_inventory_items': Inventory.objects.count(),
        }
        
        serializer = StoreStatisticsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        summary="Get store locations",
        description="Get store locations with minimal data for map display",
        responses={200: StoreLocationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='locations')
    def locations(self, request):
        """Get store locations with minimal data for map display."""
        queryset = self.get_queryset()
        
        # Apply basic filters
        is_active = request.query_params.get('is_active', '').strip()
        if is_active:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)
        
        serializer = StoreLocationSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get store inventory",
        description="Get all inventory items for a specific store",
        parameters=[
            OpenApiParameter(name='store_id', type=int, required=True, description='Store ID'),
        ]
    )
    @action(detail=True, methods=['get'], url_path='inventory')
    def store_inventory(self, request, pk=None):
        """Get all inventory items for a specific store."""
        try:
            store = self.get_object()
            inventory_items = store.inventories.all()
            
            page = self.paginate_queryset(inventory_items)
            if page is not None:
                serializer = InventoryListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = InventoryListSerializer(inventory_items, many=True)
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response(
                {'error': 'Store not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Search stores",
        description="Search stores with multiple filters including location, inventory, and other criteria",
        parameters=[
            OpenApiParameter(name='search', type=str, description='Search by store name, address, or city'),
            OpenApiParameter(name='district', type=str, description='Filter by district ID or name'),
            OpenApiParameter(name='store_type', type=str, description='Filter by store type'),
            OpenApiParameter(name='is_active', type=bool, description='Filter by active status'),
            OpenApiParameter(name='inventory_item', type=str, description='Filter stores by specific inventory item'),
            OpenApiParameter(name='latitude', type=float, description='Latitude for location-based search'),
            OpenApiParameter(name='longitude', type=float, description='Longitude for location-based search'),
            OpenApiParameter(name='radius_km', type=float, description='Search radius in kilometers (requires lat/lng)'),
            OpenApiParameter(name='sort_by_distance', type=bool, description='Sort results by distance (requires lat/lng)'),
            OpenApiParameter(name='page', type=int, description='Page number'),
            OpenApiParameter(name='limit', type=int, description='Number of results per page'),
        ],
        examples=[
            OpenApiExample(
                'Search with all filters',
                value={
                    'search': 'convenience',
                    'district': '1',
                    'store_type': 'convenience',
                    'is_active': True,
                    'inventory_item': 'Coca Cola',
                    'latitude': 10.8231,
                    'longitude': 106.6297,
                    'radius_km': 5.0,
                    'sort_by_distance': True
                },
                description='Search with location, inventory, and text filters'
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """Advanced search with multiple filters including location and inventory."""
        # Get search parameters
        search_text = request.query_params.get('search', '').strip()
        district = request.query_params.get('district', '').strip()
        store_type = request.query_params.get('store_type', '').strip()
        is_active = request.query_params.get('is_active', '').strip()
        inventory_item = request.query_params.get('inventory_item', '').strip()
        latitude = request.query_params.get('latitude', '').strip()
        longitude = request.query_params.get('longitude', '').strip()
        radius_km = request.query_params.get('radius_km', '').strip()
        sort_by_distance = request.query_params.get('sort_by_distance', '').strip()

        # Start with base queryset
        queryset = self.get_queryset()

        # Apply text search filter
        if search_text:
            search_conditions = [
                Q(name__icontains=search_text),
                Q(address__icontains=search_text),
                Q(city__icontains=search_text),
                Q(district__icontains=search_text)
            ]
            search_q = reduce(operator.or_, search_conditions)
            queryset = queryset.filter(search_q)

        # Apply district filter
        if district:
            # Try to filter by district ID first, then by name
            try:
                district_id = int(district)
                queryset = queryset.filter(district_obj_id=district_id)
            except ValueError:
                queryset = queryset.filter(
                    Q(district_obj__name__icontains=district) |
                    Q(district__icontains=district)
                )

        # Apply store type filter
        if store_type:
            queryset = queryset.filter(store_type=store_type)

        # Apply active status filter
        if is_active:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)

        # Apply inventory filter
        if inventory_item:
            # Filter stores that have the specific inventory item available
            queryset = queryset.filter(
                inventories__item__name__icontains=inventory_item,
                inventories__is_available=True
            ).distinct()

        # Apply location-based filtering and sorting
        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                user_location = Point(lng, lat, srid=4326)

                # Add distance annotation for sorting
                queryset = queryset.annotate(
                    distance=Distance('location', user_location)
                )

                # Apply radius filter if provided
                if radius_km:
                    radius = float(radius_km)
                    queryset = queryset.filter(
                        location__distance_lte=(user_location, D(km=radius))
                    )

                # Sort by distance if requested or if no radius is specified (automatic nearby sorting)
                if sort_by_distance and sort_by_distance.lower() in ['true', '1', 'yes']:
                    queryset = queryset.order_by('distance')

            except (ValueError, TypeError) as e:
                return Response(
                    {'error': f'Invalid latitude/longitude values: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Apply default ordering if no distance sorting
        if not (latitude and longitude and sort_by_distance and sort_by_distance.lower() in ['true', '1', 'yes']):
            queryset = queryset.order_by('name')

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data)
            
            # Add search metadata to response
            search_metadata = {
                'search_text': search_text,
                'filters_applied': {
                    'district': district,
                    'store_type': store_type,
                    'is_active': is_active,
                    'inventory_item': inventory_item,
                    'location_search': bool(latitude and longitude),
                    'radius_km': radius_km if radius_km else None,
                    'sort_by_distance': sort_by_distance
                }
            }
            response_data.data['search_metadata'] = search_metadata
            return response_data

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'search_metadata': {
                'search_text': search_text,
                'filters_applied': {
                    'district': district,
                    'store_type': store_type,
                    'is_active': is_active,
                    'inventory_item': inventory_item,
                    'location_search': bool(latitude and longitude),
                    'radius_km': radius_km if radius_km else None,
                    'sort_by_distance': sort_by_distance
                }
            }
        })


class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing items.
    
    Provides CRUD operations for Item model.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_active']
    search_fields = ['name', 'description', 'brand', 'barcode']
    ordering_fields = ['name', 'category', 'brand', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Optimize queryset with prefetch_related."""
        return Item.objects.prefetch_related('stores', 'inventories')

    @extend_schema(
        summary="Search items",
        description="Search items by name, category, or availability",
        parameters=[
            OpenApiParameter(name='name', type=str, description='Item name to search for'),
            OpenApiParameter(name='category', type=str, description='Item category'),
            OpenApiParameter(name='brand', type=str, description='Item brand'),
            OpenApiParameter(name='available_only', type=bool, description='Show only items available in stores'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_items(self, request):
        """Search items by various criteria."""
        name = request.query_params.get('name')
        category = request.query_params.get('category')
        brand = request.query_params.get('brand')
        available_only = request.query_params.get('available_only', 'false').lower() == 'true'
        
        queryset = self.get_queryset()
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if category:
            queryset = queryset.filter(category=category)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        if available_only:
            queryset = queryset.filter(inventories__is_available=True).distinct()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get item statistics",
        description="Get comprehensive statistics about items",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get item statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_items': queryset.count(),
            'active_items': queryset.filter(is_active=True).count(),
            'items_by_category': dict(queryset.values_list('category').annotate(count=Count('id'))),
            'items_by_brand': dict(queryset.values_list('brand').annotate(count=Count('id'))),
            'items_in_stock': queryset.filter(inventories__is_available=True).distinct().count(),
        }
        
        return Response(stats)

    @extend_schema(
        summary="Get stores for item",
        description="Get all stores that stock this item",
    )
    @action(detail=True, methods=['get'], url_path='stores')
    def item_stores(self, request, pk=None):
        """Get all stores that stock this item."""
        try:
            item = self.get_object()
            stores = item.stores.all()
            
            page = self.paginate_queryset(stores)
            if page is not None:
                serializer = StoreListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = StoreListSerializer(stores, many=True)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class InventoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing inventory entries.
    
    Provides CRUD operations for Inventory model (store-item relationships).
    """
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store', 'item', 'item__category', 'is_available']
    search_fields = ['item__name', 'store__name', 'item__brand']
    ordering_fields = ['item__name', 'created_at']
    ordering = ['item__name']

    def get_queryset(self):
        """Optimize queryset with select_related."""
        return Inventory.objects.select_related('store', 'item', 'store__district_obj')

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return InventoryListSerializer
        return InventorySerializer

    @extend_schema(
        summary="Search inventory by store location",
        description="Find inventory items in stores within a specified radius",
        parameters=[
            OpenApiParameter(name='latitude', type=float, required=True, description='Latitude coordinate'),
            OpenApiParameter(name='longitude', type=float, required=True, description='Longitude coordinate'),
            OpenApiParameter(name='radius_km', type=float, required=True, description='Search radius in kilometers'),
            OpenApiParameter(name='category', type=str, description='Filter by item category'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby_inventory(self, request):
        """Find inventory items in stores within a specified radius."""
        serializer = SpatialSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_location = Point(data['longitude'], data['latitude'], srid=4326)
        category = request.query_params.get('category')
        
        queryset = self.get_queryset().filter(
            store__location__distance_lte=(user_location, D(km=data['radius_km']))
        ).annotate(
            distance=Distance('store__location', user_location)
        )
        
        if category:
            queryset = queryset.filter(category=category)
        
        queryset = queryset.order_by('distance')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Search inventory by item",
        description="Find inventory items by name, category, or store",
        parameters=[
            OpenApiParameter(name='item_name', type=str, description='Item name to search for'),
            OpenApiParameter(name='category', type=str, description='Item category'),
            OpenApiParameter(name='available_only', type=bool, description='Show only available items'),
            OpenApiParameter(name='store', type=int, description='Filter by store ID'),
            OpenApiParameter(name='store_id', type=int, description='Filter by store ID (alias for store)'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_inventory(self, request):
        """Search inventory items by various criteria."""
        item_name = request.query_params.get('item_name')
        category = request.query_params.get('category')
        available_only = request.query_params.get('available_only', 'false').lower() == 'true'
        store_id = request.query_params.get('store_id') or request.query_params.get('store')
        
        queryset = self.get_queryset()
        
        if item_name:
            queryset = queryset.filter(item__name__icontains=item_name)
        if category:
            queryset = queryset.filter(item__category=category)
        if available_only:
            queryset = queryset.filter(is_available=True)
        if store_id:
            try:
                store_id_int = int(store_id)
                queryset = queryset.filter(store_id=store_id_int)
            except (ValueError, TypeError):
                pass  # Invalid store_id, ignore filter
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get inventory statistics",
        description="Get comprehensive statistics about inventory items",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get inventory statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_items': queryset.count(),
            'available_items': queryset.filter(is_available=True).count(),
            'unavailable_items': queryset.filter(is_available=False).count(),
            'items_by_category': dict(queryset.values_list('item__category').annotate(count=Count('id'))),
            'items_by_store': dict(queryset.values_list('store__name').annotate(count=Count('id'))),
        }
        
        return Response(stats)

    @extend_schema(
        summary="Get available inventory items",
        description="Get list of available inventory items for filtering",
        responses={200: dict}
    )
    @action(detail=False, methods=['get'], url_path='available-items')
    def available_items(self, request):
        """Get list of available inventory items."""
        items = self.get_queryset().filter(
            is_available=True
        ).values_list('item__name', flat=True).distinct().order_by('item__name')
        
        return Response({
            'items': list(items)
        })

class DistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing districts.
    
    Provides CRUD operations for District model with spatial boundary support.
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'district_type', 'is_active']
    search_fields = ['name', 'code', 'city']
    ordering_fields = ['name', 'city', 'population', 'area_km2', 'avg_income', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        return District.objects.select_related().prefetch_related('stores')

    @extend_schema(
        summary="Search districts",
        description="Search districts by various criteria",
        parameters=[
            OpenApiParameter(name='district_id', type=int, description='District ID'),
            OpenApiParameter(name='district_name', type=str, description='District name'),
            OpenApiParameter(name='district_type', type=str, description='District type (urban/suburban/rural)'),
        ],
        examples=[
            OpenApiExample(
                'Search by name',
                value={'district_name': 'District 1'},
                description='Search districts by name'
            ),
            OpenApiExample(
                'Search by type',
                value={'district_type': 'urban'},
                description='Search districts by type'
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_districts(self, request):
        """Search districts by various criteria."""
        serializer = DistrictSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = self.get_queryset()
        
        if data.get('district_id'):
            queryset = queryset.filter(id=data['district_id'])
        if data.get('district_name'):
            queryset = queryset.filter(name__icontains=data['district_name'])
        if data.get('district_type'):
            queryset = queryset.filter(district_type=data['district_type'])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get district statistics",
        description="Get comprehensive statistics about districts",
        responses={200: DistrictStatisticsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get district statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_districts': queryset.count(),
            'active_districts': queryset.filter(is_active=True).count(),
            'districts_by_type': dict(queryset.values_list('district_type').annotate(count=Count('id'))),
            'total_population': queryset.aggregate(total=Count('population'))['total'] or 0,
            'average_area': queryset.aggregate(avg=Avg('area_km2'))['avg'] or 0,
            'average_income': queryset.aggregate(avg=Avg('avg_income'))['avg'] or 0,
        }
        
        serializer = DistrictStatisticsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        summary="Lookup district by coordinates",
        description="Find the district that contains the given latitude and longitude coordinates",
        parameters=[
            OpenApiParameter(name='latitude', type=float, required=True, description='Latitude coordinate'),
            OpenApiParameter(name='longitude', type=float, required=True, description='Longitude coordinate'),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'district': {'type': 'string', 'description': 'District name'},
                    'district_id': {'type': 'integer', 'description': 'District ID'},
                    'district_type': {'type': 'string', 'description': 'District type'},
                    'city': {'type': 'string', 'description': 'City name'},
                    'found': {'type': 'boolean', 'description': 'Whether a district was found'},
                }
            },
            400: {'description': 'Invalid coordinates provided'}
        },
        examples=[
            OpenApiExample(
                'Lookup district',
                value={'latitude': 10.8231, 'longitude': 106.6297},
                description='Find district containing the coordinates'
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='lookup-by-coordinates')
    def lookup_by_coordinates(self, request):
        """Find the district that contains the given coordinates."""
        try:
            # Get coordinates from query parameters
            latitude = request.query_params.get('latitude')
            longitude = request.query_params.get('longitude')
            
            if not latitude or not longitude:
                return Response(
                    {'error': 'Both latitude and longitude parameters are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                lat = float(latitude)
                lng = float(longitude)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid latitude or longitude values'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate coordinate ranges
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return Response(
                    {'error': 'Latitude must be between -90 and 90, longitude between -180 and 180'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create point from coordinates
            point = Point(lng, lat, srid=4326)
            
            # Find district that contains this point using spatial query
            district = District.objects.filter(
                boundary__contains=point,
                is_active=True
            ).first()
            
            if district:
                return Response({
                    'district': district.name,
                    'district_id': district.id,
                    'district_type': district.district_type,
                    'city': district.city,
                    'found': True
                })
            else:
                # No district found, return "Other"
                return Response({
                    'district': 'Other',
                    'district_id': None,
                    'district_type': 'other',
                    'city': 'Ho Chi Minh City',
                    'found': False
                })
                
        except Exception as e:
            return Response(
                {'error': f'Error processing coordinates: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AnalyticsView(APIView):
    """
    API endpoint for comprehensive analytics data.
    
    Provides all analytics calculations in a single endpoint for better performance.
    """
    
    @extend_schema(
        summary="Get comprehensive analytics data",
        description="Get comprehensive analytics including stores, districts, and inventory statistics",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'totalStores': {'type': 'integer', 'description': 'Total number of stores'},
                    'activeStores': {'type': 'integer', 'description': 'Number of active stores'},
                    'inactiveStores': {'type': 'integer', 'description': 'Number of inactive stores'},
                    'totalDistricts': {'type': 'integer', 'description': 'Total number of districts'},
                    'totalInventoryItems': {'type': 'integer', 'description': 'Total inventory items'},
                    'availableInventoryItems': {'type': 'integer', 'description': 'Available inventory items'},
                    'unavailableInventoryItems': {'type': 'integer', 'description': 'Unavailable inventory items'},
                    'storesByDistrict': {'type': 'object', 'description': 'Stores count by district'},
                    'storesByType': {'type': 'object', 'description': 'Stores count by type/brand'},
                    'averageStoresPerDistrict': {'type': 'number', 'description': 'Average stores per district'},
                    'topDistricts': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        },
                        'description': 'Top 5 districts by store count'
                    },
                    'inventoryAvailabilityRate': {'type': 'number', 'description': 'Inventory availability percentage'},
                    'topStoreTypes': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string'},
                                'count': {'type': 'integer'},
                                'percentage': {'type': 'number'}
                            }
                        },
                        'description': 'Top store types/brands with counts and percentages'
                    },
                    'inventoryByCategory': {'type': 'object', 'description': 'Inventory items count by category'},
                    'totalItems': {'type': 'integer', 'description': 'Total unique items in catalog'},
                    'averageInventoryPerStore': {'type': 'number', 'description': 'Average inventory items per store'},
                }
            }
        }
    )
    def get(self, request):
        """Get comprehensive analytics data."""
        try:
            # Get basic counts using efficient queries
            total_stores = Store.objects.count()
            active_stores = Store.objects.filter(is_active=True).count()
            inactive_stores = total_stores - active_stores
            total_districts = District.objects.count()
            total_inventory_items = Inventory.objects.count()
            available_inventory_items = Inventory.objects.filter(is_available=True).count()
            unavailable_inventory_items = total_inventory_items - available_inventory_items
            total_items = Item.objects.count()
            
            # Stores by district - use database aggregation
            stores_by_district_raw = Store.objects.values('district').annotate(
                count=Count('id')
            ).order_by('-count')
            
            stores_by_district = {}
            for item in stores_by_district_raw:
                district_name = item['district'] or 'Unknown'
                stores_by_district[district_name] = item['count']
            
            # Stores by type/brand - use database aggregation
            stores_by_type_raw = Store.objects.values('store_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            stores_by_type = {}
            for item in stores_by_type_raw:
                store_type = item['store_type'] or 'unknown'
                stores_by_type[store_type] = item['count']
            
            # Top districts (top 5)
            top_districts = [
                {'name': district, 'count': count}
                for district, count in sorted(stores_by_district.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Top store types with percentages
            top_store_types = []
            for store_type, count in sorted(stores_by_type.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_stores * 100) if total_stores > 0 else 0
                top_store_types.append({
                    'type': store_type,
                    'count': count,
                    'percentage': round(percentage, 1)
                })
            
            # Inventory by category - use database aggregation through join
            inventory_by_category_raw = Inventory.objects.select_related('item').values(
                'item__category'
            ).annotate(count=Count('id')).order_by('-count')
            
            inventory_by_category = {}
            for item in inventory_by_category_raw:
                category = item['item__category'] or 'other'
                inventory_by_category[category] = item['count']
            
            # Calculate rates and averages
            average_stores_per_district = total_stores / total_districts if total_districts > 0 else 0
            inventory_availability_rate = (available_inventory_items / total_inventory_items * 100) if total_inventory_items > 0 else 0
            average_inventory_per_store = total_inventory_items / total_stores if total_stores > 0 else 0
            
            # Prepare response data
            analytics_data = {
                'totalStores': total_stores,
                'activeStores': active_stores,
                'inactiveStores': inactive_stores,
                'totalDistricts': total_districts,
                'totalInventoryItems': total_inventory_items,
                'availableInventoryItems': available_inventory_items,
                'unavailableInventoryItems': unavailable_inventory_items,
                'storesByDistrict': stores_by_district,
                'storesByType': stores_by_type,
                'averageStoresPerDistrict': round(average_stores_per_district, 2),
                'topDistricts': top_districts,
                'inventoryAvailabilityRate': round(inventory_availability_rate, 1),
                'topStoreTypes': top_store_types,
                'inventoryByCategory': inventory_by_category,
                'totalItems': total_items,
                'averageInventoryPerStore': round(average_inventory_per_store, 1),
            }
            
            return Response(analytics_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch analytics data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StatisticsView(APIView):
    """Placeholder view for statistics - to be implemented"""
    def get(self, request):
        return Response({
            'message': 'Statistics endpoint - to be implemented',
            'status': 'success'
        }, status=status.HTTP_200_OK)

class SpatialSearchView(APIView):
    """Placeholder view for spatial search - to be implemented"""
    def get(self, request):
        return Response({
            'message': 'Spatial search endpoint - to be implemented',
            'status': 'success'
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
def store_list(request):
    """Placeholder view for store list"""
    return Response({
        'message': 'Store list endpoint - to be implemented',
        'status': 'success'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def store_detail(request, store_id):
    """Placeholder view for store detail"""
    return Response({
        'message': f'Store detail endpoint for store {store_id} - to be implemented',
        'status': 'success'
    }, status=status.HTTP_200_OK) 