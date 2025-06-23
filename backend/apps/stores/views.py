"""
Django REST framework API views for the stores app with spatial querying support.
"""

from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Count, Avg, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Store, Inventory, District
from .serializers import StoreSerializer, InventorySerializer, DistrictSerializer, StoreListSerializer, InventoryListSerializer, SpatialSearchSerializer, DistrictSearchSerializer, StoreStatisticsSerializer, DistrictStatisticsSerializer

class StoreViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing stores.
    
    Provides CRUD operations for Store model with spatial location support.
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
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
        summary="Search stores by location",
        description="Find stores within a specified radius from given coordinates",
        parameters=[
            OpenApiParameter(name='latitude', type=float, required=True, description='Latitude coordinate'),
            OpenApiParameter(name='longitude', type=float, required=True, description='Longitude coordinate'),
            OpenApiParameter(name='radius_km', type=float, required=True, description='Search radius in kilometers'),
        ],
        examples=[
            OpenApiExample(
                'Search near Ho Chi Minh City center',
                value={'latitude': 10.8231, 'longitude': 106.6297, 'radius_km': 5.0},
                description='Find stores within 5km of Ho Chi Minh City center'
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby_stores(self, request):
        """Find stores within a specified radius from given coordinates."""
        serializer = SpatialSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_location = Point(data['longitude'], data['latitude'], srid=4326)
        
        queryset = self.get_queryset().filter(
            location__distance_lte=(user_location, D(km=data['radius_km']))
        ).annotate(
            distance=Distance('location', user_location)
        ).order_by('distance')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Search stores in district",
        description="Find stores within a specific district",
        parameters=[
            OpenApiParameter(name='district_id', type=int, description='District ID'),
            OpenApiParameter(name='district_name', type=str, description='District name'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='in-district')
    def stores_in_district(self, request):
        """Find stores within a specific district."""
        district_id = request.query_params.get('district_id')
        district_name = request.query_params.get('district_name')
        
        queryset = self.get_queryset()
        
        if district_id:
            queryset = queryset.filter(district_obj_id=district_id)
        elif district_name:
            queryset = queryset.filter(district_obj__name__icontains=district_name)
        else:
            return Response(
                {'error': 'Either district_id or district_name must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

class InventoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing inventory items.
    
    Provides CRUD operations for Inventory model.
    """
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store', 'category', 'is_available']
    search_fields = ['item_name', 'store__name']
    ordering_fields = ['item_name', 'quantity', 'price', 'created_at']
    ordering = ['item_name']

    def get_queryset(self):
        """Optimize queryset with select_related."""
        return Inventory.objects.select_related('store', 'store__district_obj')

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
        description="Find inventory items by name or category",
        parameters=[
            OpenApiParameter(name='item_name', type=str, description='Item name to search for'),
            OpenApiParameter(name='category', type=str, description='Item category'),
            OpenApiParameter(name='available_only', type=bool, description='Show only available items'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_inventory(self, request):
        """Search inventory items by various criteria."""
        item_name = request.query_params.get('item_name')
        category = request.query_params.get('category')
        available_only = request.query_params.get('available_only', 'false').lower() == 'true'
        
        queryset = self.get_queryset()
        
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)
        if category:
            queryset = queryset.filter(category=category)
        if available_only:
            queryset = queryset.filter(is_available=True)
        
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
            'items_by_category': dict(queryset.values_list('category').annotate(count=Count('id'))),
            'items_by_store': dict(queryset.values_list('store__name').annotate(count=Count('id'))),
            'average_price': queryset.aggregate(avg=Avg('price'))['avg'] or 0,
            'total_quantity': queryset.aggregate(total=Count('quantity'))['total'] or 0,
        }
        
        return Response(stats)

class DistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing districts.
    
    Provides CRUD operations for District model with spatial boundary support.
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
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