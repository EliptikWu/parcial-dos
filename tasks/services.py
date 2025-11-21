"""
Services layer for Task Management API.
Contains business logic separated from views.
"""
from typing import List, Optional
from django.db.models import QuerySet
from .models import User, Task


class UserService:
    """Service class for User-related business logic."""

    @staticmethod
    def create_user(name: str, email: str) -> User:
        """
        Create a new user.
        
        Args:
            name: User's name
            email: User's email address
            
        Returns:
            User: Created user instance
        """
        user = User.objects.create(name=name, email=email)
        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User or None if not found
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_all_users() -> QuerySet[User]:
        """
        Get all users.
        
        Returns:
            QuerySet of all users
        """
        return User.objects.all()

    @staticmethod
    def update_user(user_id: int, **kwargs) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: User's ID
            **kwargs: Fields to update
            
        Returns:
            Updated user or None if not found
        """
        user = UserService.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            user.save()
        return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            True if deleted, False if not found
        """
        user = UserService.get_user_by_id(user_id)
        if user:
            user.delete()
            return True
        return False


class TaskService:
    """Service class for Task-related business logic."""

    @staticmethod
    def create_task(title: str, user_id: int, description: str = "") -> Optional[Task]:
        """
        Create a new task for a user.
        
        Args:
            title: Task title
            user_id: ID of the user who owns the task
            description: Optional task description
            
        Returns:
            Task: Created task instance or None if user doesn't exist
        """
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        
        task = Task.objects.create(
            title=title,
            description=description,
            user=user
        )
        return task

    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: Task's ID
            
        Returns:
            Task or None if not found
        """
        try:
            return Task.objects.select_related('user').get(id=task_id)
        except Task.DoesNotExist:
            return None

    @staticmethod
    def get_tasks_by_user(user_id: int) -> QuerySet[Task]:
        """
        Get all tasks for a specific user.
        
        Args:
            user_id: User's ID
            
        Returns:
            QuerySet of tasks
        """
        return Task.objects.filter(user_id=user_id).select_related('user')

    @staticmethod
    def get_all_tasks() -> QuerySet[Task]:
        """
        Get all tasks.
        
        Returns:
            QuerySet of all tasks
        """
        return Task.objects.select_related('user').all()

    @staticmethod
    def update_task(task_id: int, **kwargs) -> Optional[Task]:
        """
        Update task information.
        
        Args:
            task_id: Task's ID
            **kwargs: Fields to update (title, description, is_completed)
            
        Returns:
            Updated task or None if not found
        """
        task = TaskService.get_task_by_id(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.save()
        return task

    @staticmethod
    def toggle_task_completion(task_id: int) -> Optional[Task]:
        """
        Toggle task completion status.
        
        Args:
            task_id: Task's ID
            
        Returns:
            Updated task or None if not found
        """
        task = TaskService.get_task_by_id(task_id)
        if task:
            task.is_completed = not task.is_completed
            task.save()
        return task

    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task's ID
            
        Returns:
            True if deleted, False if not found
        """
        task = TaskService.get_task_by_id(task_id)
        if task:
            task.delete()
            return True
        return False

    @staticmethod
    def get_completed_tasks(user_id: Optional[int] = None) -> QuerySet[Task]:
        """
        Get completed tasks, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            QuerySet of completed tasks
        """
        queryset = Task.objects.filter(is_completed=True).select_related('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @staticmethod
    def get_pending_tasks(user_id: Optional[int] = None) -> QuerySet[Task]:
        """
        Get pending (incomplete) tasks, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            QuerySet of pending tasks
        """
        queryset = Task.objects.filter(is_completed=False).select_related('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset