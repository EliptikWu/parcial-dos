from rest_framework import serializers
from .models import User, Task


class UserSerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'tasks_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'is_completed',
            'user', 'user_name', 'user_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        """Validate that title is not empty."""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'user']

    def validate_title(self, value):
        """Validate that title is not empty."""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating task status."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'is_completed']

    def validate_title(self, value):
        """Validate that title is not empty if provided."""
        if value is not None and value.strip() == '':
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value