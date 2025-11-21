"""
Unit tests for models and services.
"""
import pytest
from django.db.utils import IntegrityError
from tasks.models import User, Task
from tasks.services import UserService, TaskService


@pytest.mark.unit
@pytest.mark.django_db
class TestUserModel:
    """Unit tests for User model."""

    def test_create_user(self):
        """Test user creation."""
        user = User.objects.create(name="John Doe", email="john@example.com")
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.id is not None

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create(name="Jane Smith", email="jane@example.com")
        assert str(user) == "Jane Smith (jane@example.com)"

    def test_user_email_unique(self):
        """Test that email must be unique."""
        User.objects.create(name="User 1", email="duplicate@example.com")
        with pytest.raises(IntegrityError):
            User.objects.create(name="User 2", email="duplicate@example.com")

    def test_user_tasks_relationship(self, user):
        """Test that user has tasks relationship."""
        Task.objects.create(title="Task 1", user=user)
        Task.objects.create(title="Task 2", user=user)
        assert user.tasks.count() == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestTaskModel:
    """Unit tests for Task model."""

    def test_create_task(self, user):
        """Test task creation."""
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            user=user
        )
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.is_completed is False
        assert task.user == user

    def test_task_default_is_completed(self, user):
        """Test that is_completed defaults to False."""
        task = Task.objects.create(title="Task", user=user)
        assert task.is_completed is False

    def test_task_str_representation(self, user):
        """Test task string representation."""
        task = Task.objects.create(title="My Task", user=user)
        assert "○ My Task" in str(task)
        
        task.is_completed = True
        task.save()
        assert "✓ My Task" in str(task)

    def test_task_cascade_delete(self, user):
        """Test that tasks are deleted when user is deleted."""
        Task.objects.create(title="Task 1", user=user)
        Task.objects.create(title="Task 2", user=user)
        assert Task.objects.count() == 2
        
        user.delete()
        assert Task.objects.count() == 0


@pytest.mark.unit
@pytest.mark.django_db
class TestUserService:
    """Unit tests for UserService."""

    def test_create_user(self):
        """Test creating a user through service."""
        user = UserService.create_user(name="Alice", email="alice@example.com")
        assert user.name == "Alice"
        assert user.email == "alice@example.com"
        assert User.objects.count() == 1

    def test_get_user_by_id(self, user):
        """Test retrieving user by ID."""
        retrieved_user = UserService.get_user_by_id(user.id)
        assert retrieved_user == user

    def test_get_user_by_id_not_found(self):
        """Test retrieving non-existent user."""
        retrieved_user = UserService.get_user_by_id(9999)
        assert retrieved_user is None

    def test_get_all_users(self, multiple_users):
        """Test getting all users."""
        users = UserService.get_all_users()
        assert users.count() == 3

    def test_update_user(self, user):
        """Test updating user information."""
        updated_user = UserService.update_user(
            user.id,
            name="Updated Name",
            email="updated@example.com"
        )
        assert updated_user.name == "Updated Name"
        assert updated_user.email == "updated@example.com"

    def test_delete_user(self, user):
        """Test deleting a user."""
        user_id = user.id
        deleted = UserService.delete_user(user_id)
        assert deleted is True
        assert UserService.get_user_by_id(user_id) is None


@pytest.mark.unit
@pytest.mark.django_db
class TestTaskService:
    """Unit tests for TaskService."""

    def test_create_task(self, user):
        """Test creating a task through service."""
        task = TaskService.create_task(
            title="Service Task",
            user_id=user.id,
            description="Task description"
        )
        assert task.title == "Service Task"
        assert task.description == "Task description"
        assert task.user == user

    def test_create_task_invalid_user(self):
        """Test creating task with non-existent user."""
        task = TaskService.create_task(
            title="Task",
            user_id=9999,
            description="Description"
        )
        assert task is None

    def test_get_task_by_id(self, task):
        """Test retrieving task by ID."""
        retrieved_task = TaskService.get_task_by_id(task.id)
        assert retrieved_task == task

    def test_get_tasks_by_user(self, user, multiple_tasks):
        """Test getting all tasks for a user."""
        tasks = TaskService.get_tasks_by_user(user.id)
        assert tasks.count() == 3

    def test_update_task(self, task):
        """Test updating task information."""
        updated_task = TaskService.update_task(
            task.id,
            title="Updated Task",
            is_completed=True
        )
        assert updated_task.title == "Updated Task"
        assert updated_task.is_completed is True

    def test_toggle_task_completion(self, task):
        """Test toggling task completion status."""
        assert task.is_completed is False
        
        toggled_task = TaskService.toggle_task_completion(task.id)
        assert toggled_task.is_completed is True
        
        toggled_task = TaskService.toggle_task_completion(task.id)
        assert toggled_task.is_completed is False

    def test_delete_task(self, task):
        """Test deleting a task."""
        task_id = task.id
        deleted = TaskService.delete_task(task_id)
        assert deleted is True
        assert TaskService.get_task_by_id(task_id) is None

    def test_get_completed_tasks(self, user, multiple_tasks):
        """Test getting completed tasks."""
        completed_tasks = TaskService.get_completed_tasks()
        assert completed_tasks.count() == 1
        assert all(task.is_completed for task in completed_tasks)

    def test_get_pending_tasks(self, user, multiple_tasks):
        """Test getting pending tasks."""
        pending_tasks = TaskService.get_pending_tasks()
        assert pending_tasks.count() == 2
        assert all(not task.is_completed for task in pending_tasks)