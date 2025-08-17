"""
URL configuration for the stores app API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from backend.apps.stores.views import DistrictViewSet, StoreViewSet, ItemViewSet, InventoryViewSet, ReviewViewSet, AnalyticsView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'districts', DistrictViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'items', ItemViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'reviews', ReviewViewSet)

app_name = 'stores'

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Analytics endpoint
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    
    # API documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='stores:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='stores:schema'), name='redoc'),
] 