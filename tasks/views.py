"""
Views/Controllers for Task Management API.
Handles HTTP requests and responses using ViewSets.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, Task
from .serializers import (
    UserSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer
)
from .services import UserService, TaskService


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations.
    Provides CRUD operations for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """Create a new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.create_user(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email']
        )
        
        output_serializer = self.get_serializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update user information."""
        user_id = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.update_user(user_id, **serializer.validated_data)
        
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        output_serializer = self.get_serializer(user)
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a user."""
        user_id = kwargs.get('pk')
        deleted = UserService.delete_user(user_id)
        
        if not deleted:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        method='get',
        responses={200: TaskSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for a specific user."""
        tasks = TaskService.get_tasks_by_user(pk)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task operations.
    Provides CRUD operations for tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def create(self, request, *args, **kwargs):
        """Create a new task."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task = TaskService.create_task(
            title=serializer.validated_data['title'],
            user_id=serializer.validated_data['user'].id,
            description=serializer.validated_data.get('description', '')
        )
        
        if not task:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        output_serializer = TaskSerializer(task)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update task information."""
        task_id = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        task = TaskService.update_task(task_id, **serializer.validated_data)
        
        if not task:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        output_serializer = TaskSerializer(task)
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a task."""
        task_id = kwargs.get('pk')
        deleted = TaskService.delete_task(task_id)
        
        if not deleted:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={200: TaskSerializer()}
    )
    @action(detail=True, methods=['post'])
    def toggle_completion(self, request, pk=None):
        """Toggle task completion status."""
        task = TaskService.toggle_task_completion(pk)
        
        if not task:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="Filter by user ID",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={200: TaskSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get all completed tasks, optionally filtered by user."""
        user_id = request.query_params.get('user_id')
        tasks = TaskService.get_completed_tasks(user_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="Filter by user ID",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={200: TaskSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending tasks, optionally filtered by user."""
        user_id = request.query_params.get('user_id')
        tasks = TaskService.get_pending_tasks(user_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)