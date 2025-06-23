"""
Main API URL configuration for convenience store management system.
"""
from django.urls import path, include

urlpatterns = [
    path('v1/', include('backend.apps.stores.urls')),
] 