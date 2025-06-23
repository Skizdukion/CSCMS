"""
URL configuration for the stores app API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from backend.apps.stores.views import DistrictViewSet, StoreViewSet, InventoryViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'districts', DistrictViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'inventory', InventoryViewSet)

app_name = 'stores'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='stores:schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='stores:schema'), name='redoc'),
    
    # Include DRF authentication URLs
    path('api-auth/', include('rest_framework.urls')),
] 