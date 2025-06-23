"""
Spatial utility functions for performance-optimized geographic operations.
"""
from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Point
from django.db.models import Q, Count, Avg
from django.contrib.gis.db.models.functions import Distance
from ..models import Store, District, Inventory


def get_stores_within_radius(center_point, radius_km, store_type=None, is_active=True):
    """
    Get stores within a specified radius with performance optimization.
    
    Args:
        center_point: Point object (longitude, latitude)
        radius_km: Radius in kilometers
        store_type: Optional store type filter
        is_active: Filter for active stores only
    
    Returns:
        QuerySet of stores within radius, ordered by distance
    """
    # Convert km to degrees (approximate)
    radius_degrees = radius_km / 111.32
    
    # Build query with spatial index optimization
    query: Q = Q(location__distance_lte=(center_point, radius_degrees))
    
    if store_type:
        query &= Q(store_type=store_type)  # type: ignore
    if is_active:
        query = query & Q(is_active=True)  # type: ignore
    
    return Store.objects.filter(query).annotate(  # type: ignore
        distance=Distance('location', center_point)
    ).order_by('distance')


def get_stores_by_district(district_name=None, district_obj=None, store_type=None):
    """
    Get stores by district with optimized queries.
    
    Args:
        district_name: District name string
        district_obj: District object
        store_type: Optional store type filter
    
    Returns:
        QuerySet of stores in district
    """
    query = Q()
    
    if district_obj and district_obj.boundary:
        # Use spatial query if boundary exists
        query = Q(location__within=district_obj.boundary)
    elif district_name:
        # Fallback to name-based query
        query = Q(district=district_name)
    elif district_obj:
        # Use foreign key relationship
        query = Q(district_obj=district_obj)
    
    if store_type:
        query &= Q(store_type=store_type)
    
    return Store.objects.filter(query).select_related('district_obj')  # type: ignore


def get_store_density_by_district():
    """
    Calculate store density by district for performance analysis.
    
    Returns:
        QuerySet with district info and store counts
    """
    return District.objects.annotate(  # type: ignore
        store_count=Count('stores'),
        avg_rating=Avg('stores__rating')
    ).filter(is_active=True).order_by('-store_count')


def get_nearest_stores(target_point, limit=10, store_type=None):
    """
    Find nearest stores to a target point with performance optimization.
    
    Args:
        target_point: Point object (longitude, latitude)
        limit: Maximum number of stores to return
        store_type: Optional store type filter
    
    Returns:
        QuerySet of nearest stores with distances
    """
    query = Q(location__isnull=False) & Q(is_active=True)
    
    if store_type:
        query &= Q(store_type=store_type)  # type: ignore
    
    return Store.objects.filter(query).annotate(  # type: ignore
        distance=Distance('location', target_point)
    ).order_by('distance')[:limit]


def get_spatial_statistics():
    """
    Get comprehensive spatial statistics for performance monitoring.
    
    Returns:
        Dictionary with spatial statistics
    """
    stats = {}
    
    # Store distribution by district
    stats['stores_by_district'] = list(
        District.objects.annotate(  # type: ignore
            store_count=Count('stores')
        ).values('name', 'store_count').order_by('-store_count')
    )
    
    # Store distribution by type
    stats['stores_by_type'] = list(
        Store.objects.values('store_type').annotate(  # type: ignore
            count=Count('id')
        ).order_by('-count')
    )
    
    # Geographic extent
    extent = Store.objects.filter(location__isnull=False).aggregate(  # type: ignore
        extent=Extent('location')
    )
    stats['geographic_extent'] = extent.get('extent')
    
    # Average store density
    total_stores = Store.objects.filter(is_active=True).count()  # type: ignore
    total_districts = District.objects.filter(is_active=True).count()  # type: ignore
    stats['avg_stores_per_district'] = total_stores / total_districts if total_districts > 0 else 0
    
    return stats


def optimize_spatial_queries():
    """
    Utility function to provide hints for spatial query optimization.
    
    Returns:
        Dictionary with optimization recommendations
    """
    return {
        'spatial_indexes': [
            'Store.location (PointField with spatial_index=True)',
            'District.boundary (PolygonField with spatial_index=True)',
        ],
        'composite_indexes': [
            'Store: (is_active, store_type, city)',
            'Store: (district_obj, store_type)',
            'Inventory: (store, category, is_available)',
            'District: (is_active, district_type)',
        ],
        'query_optimizations': [
            'Use spatial indexes for distance and containment queries',
            'Use select_related() for foreign key relationships',
            'Use prefetch_related() for reverse foreign key relationships',
            'Filter by is_active before spatial operations',
            'Use Distance annotation for nearest neighbor queries',
        ],
        'performance_tips': [
            'Limit spatial query results with [:limit]',
            'Use bounding box queries before precise spatial operations',
            'Cache frequently accessed spatial data',
            'Use database-level spatial functions when possible',
        ]
    } 