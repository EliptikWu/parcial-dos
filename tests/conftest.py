"""
Pytest configuration and fixtures.
"""
import pytest
from rest_framework.test import APIClient
from tasks.models import User, Task


@pytest.fixture
def api_client():
    """Fixture for DRF API client."""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture factory for creating users."""
    def _create_user(**kwargs):
        defaults = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        defaults.update(kwargs)
        return User.objects.create(**defaults)
    return _create_user


@pytest.fixture
def user(create_user):
    """Fixture for a single test user."""
    return create_user()


@pytest.fixture
def create_task():
    """Fixture factory for creating tasks."""
    def _create_task(user, **kwargs):
        defaults = {
            'title': 'Test Task',
            'description': 'Test Description',
            'is_completed': False
        }
        defaults.update(kwargs)
        return Task.objects.create(user=user, **defaults)
    return _create_task


@pytest.fixture
def task(user, create_task):
    """Fixture for a single test task."""
    return create_task(user)


@pytest.fixture
def multiple_users(create_user):
    """Fixture for multiple test users."""
    return [
        create_user(name='User 1', email='user1@example.com'),
        create_user(name='User 2', email='user2@example.com'),
        create_user(name='User 3', email='user3@example.com'),
    ]


@pytest.fixture
def multiple_tasks(user, create_task):
    """Fixture for multiple test tasks."""
    return [
        create_task(user, title='Task 1', is_completed=False),
        create_task(user, title='Task 2', is_completed=True),
        create_task(user, title='Task 3', is_completed=False),
    ]