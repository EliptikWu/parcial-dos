"""
URL routing for Task Management API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TaskViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]