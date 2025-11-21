"""
Integration tests for API endpoints.
"""
import pytest
from rest_framework import status
from tasks.models import User, Task


@pytest.mark.integration
@pytest.mark.django_db
class TestUserEndpoints:
    """Integration tests for User endpoints."""

    def test_create_user(self, api_client):
        """Test POST /api/users/"""
        data = {
            'name': 'New User',
            'email': 'newuser@example.com'
        }
        response = api_client.post('/api/users/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New User'
        assert response.data['email'] == 'newuser@example.com'
        assert 'id' in response.data

    def test_create_user_duplicate_email(self, api_client, user):
        """Test creating user with duplicate email."""
        data = {
            'name': 'Another User',
            'email': user.email
        }
        response = api_client.post('/api/users/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_users(self, api_client, multiple_users):
        """Test GET /api/users/"""
        response = api_client.get('/api/users/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_retrieve_user(self, api_client, user):
        """Test GET /api/users/{id}/"""
        response = api_client.get(f'/api/users/{user.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['name'] == user.name
        assert response.data['email'] == user.email

    def test_update_user(self, api_client, user):
        """Test PUT /api/users/{id}/"""
        data = {
            'name': 'Updated Name',
            'email': 'updated@example.com'
        }
        response = api_client.put(f'/api/users/{user.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Name'
        assert response.data['email'] == 'updated@example.com'

    def test_partial_update_user(self, api_client, user):
        """Test PATCH /api/users/{id}/"""
        data = {'name': 'Patched Name'}
        response = api_client.patch(f'/api/users/{user.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Patched Name'
        assert response.data['email'] == user.email

    def test_delete_user(self, api_client, user):
        """Test DELETE /api/users/{id}/"""
        response = api_client.delete(f'/api/users/{user.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=user.id).exists()

    def test_get_user_tasks(self, api_client, user, multiple_tasks):
        """Test GET /api/users/{id}/tasks/"""
        response = api_client.get(f'/api/users/{user.id}/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3


@pytest.mark.integration
@pytest.mark.django_db
class TestTaskEndpoints:
    """Integration tests for Task endpoints."""

    def test_create_task(self, api_client, user):
        """Test POST /api/tasks/"""
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'user': user.id
        }
        response = api_client.post('/api/tasks/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert response.data['description'] == 'Task description'
        assert response.data['is_completed'] is False
        assert response.data['user'] == user.id

    def test_create_task_invalid_user(self, api_client):
        """Test creating task with invalid user ID."""
        data = {
            'title': 'Task',
            'description': 'Description',
            'user': 9999
        }
        response = api_client.post('/api/tasks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_task_empty_title(self, api_client, user):
        """Test creating task with empty title."""
        data = {
            'title': '',
            'user': user.id
        }
        response = api_client.post('/api/tasks/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_tasks(self, api_client, user, multiple_tasks):
        """Test GET /api/tasks/"""
        response = api_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_retrieve_task(self, api_client, task):
        """Test GET /api/tasks/{id}/"""
        response = api_client.get(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == task.id
        assert response.data['title'] == task.title

    def test_update_task(self, api_client, task):
        """Test PUT /api/tasks/{id}/"""
        data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'is_completed': True
        }
        response = api_client.put(f'/api/tasks/{task.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Task'
        assert response.data['is_completed'] is True

    def test_partial_update_task(self, api_client, task):
        """Test PATCH /api/tasks/{id}/"""
        data = {'is_completed': True}
        response = api_client.patch(f'/api/tasks/{task.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is True
        assert response.data['title'] == task.title

    def test_delete_task(self, api_client, task):
        """Test DELETE /api/tasks/{id}/"""
        response = api_client.delete(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()

    def test_toggle_task_completion(self, api_client, task):
        """Test POST /api/tasks/{id}/toggle_completion/"""
        # Initially not completed
        assert task.is_completed is False
        
        response = api_client.post(f'/api/tasks/{task.id}/toggle_completion/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is True
        
        # Toggle again
        response = api_client.post(f'/api/tasks/{task.id}/toggle_completion/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is False

    def test_get_completed_tasks(self, api_client, user, multiple_tasks):
        """Test GET /api/tasks/completed/"""
        response = api_client.get('/api/tasks/completed/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert all(task['is_completed'] for task in response.data)

    def test_get_pending_tasks(self, api_client, user, multiple_tasks):
        """Test GET /api/tasks/pending/"""
        response = api_client.get('/api/tasks/pending/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert all(not task['is_completed'] for task in response.data)

    def test_filter_completed_tasks_by_user(self, api_client, user, multiple_tasks):
        """Test GET /api/tasks/completed/?user_id={user_id}"""
        response = api_client.get(f'/api/tasks/completed/?user_id={user.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert all(task['user'] == user.id for task in response.data)