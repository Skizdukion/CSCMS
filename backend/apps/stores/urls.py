"""
URL configuration for stores app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stores', views.StoreViewSet)
router.register(r'inventory', views.InventoryViewSet)
router.register(r'districts', views.DistrictViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('spatial-search/', views.SpatialSearchView.as_view(), name='spatial-search'),
] 