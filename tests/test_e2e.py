"""
End-to-end tests that validate complete user workflows.
"""
import pytest
from rest_framework import status


@pytest.mark.e2e
@pytest.mark.django_db
class TestCompleteUserTaskFlow:
    """
    End-to-end test that validates a complete workflow:
    1. Create a user
    2. Create tasks for that user
    3. Update task status
    4. List user's tasks
    5. Mark tasks as completed
    6. Delete tasks
    7. Delete user
    """

    def test_complete_task_management_workflow(self, api_client):
        """Test a complete task management workflow from start to finish."""
        
        # Step 1: Create a new user
        print("\n=== Step 1: Creating user ===")
        user_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
        response = api_client.post('/api/users/', user_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        user_id = response.data['id']
        print(f"✓ User created with ID: {user_id}")
        
        # Step 2: Create multiple tasks for the user
        print("\n=== Step 2: Creating tasks ===")
        tasks_data = [
            {'title': 'Buy groceries', 'description': 'Milk, eggs, bread', 'user': user_id},
            {'title': 'Finish project', 'description': 'Complete Django API', 'user': user_id},
            {'title': 'Gym workout', 'description': 'Chest and triceps', 'user': user_id},
        ]
        
        task_ids = []
        for task_data in tasks_data:
            response = api_client.post('/api/tasks/', task_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['is_completed'] is False
            task_ids.append(response.data['id'])
            print(f"✓ Task created: {task_data['title']}")
        
        assert len(task_ids) == 3
        
        # Step 3: Verify all tasks were created for the user
        print("\n=== Step 3: Listing user's tasks ===")
        response = api_client.get(f'/api/users/{user_id}/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        print(f"✓ User has {len(response.data)} tasks")
        
        # Step 4: Update the first task's title and description
        print("\n=== Step 4: Updating task ===")
        update_data = {
            'title': 'Buy groceries (UPDATED)',
            'description': 'Milk, eggs, bread, cheese',
        }
        response = api_client.patch(f'/api/tasks/{task_ids[0]}/', update_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == update_data['title']
        assert response.data['description'] == update_data['description']
        print(f"✓ Task updated: {response.data['title']}")
        
        # Step 5: Mark first task as completed using toggle
        print("\n=== Step 5: Marking task as completed ===")
        response = api_client.post(f'/api/tasks/{task_ids[0]}/toggle_completion/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is True
        print(f"✓ Task marked as completed")
        
        # Step 6: Mark second task as completed using PATCH
        response = api_client.patch(
            f'/api/tasks/{task_ids[1]}/',
            {'is_completed': True},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is True
        print(f"✓ Second task marked as completed")
        
        # Step 7: Verify completed tasks count
        print("\n=== Step 6: Checking completed tasks ===")
        response = api_client.get('/api/tasks/completed/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        print(f"✓ Found {len(response.data)} completed tasks")
        
        # Step 8: Verify pending tasks count
        print("\n=== Step 7: Checking pending tasks ===")
        response = api_client.get('/api/tasks/pending/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        print(f"✓ Found {len(response.data)} pending task")
        
        # Step 9: Get all tasks and verify states
        print("\n=== Step 8: Verifying all tasks ===")
        response = api_client.get('/api/tasks/')
        assert response.status_code == status.HTTP_200_OK
        tasks = response.data['results']
        completed_count = sum(1 for task in tasks if task['is_completed'])
        pending_count = sum(1 for task in tasks if not task['is_completed'])
        assert completed_count == 2
        assert pending_count == 1
        print(f"✓ Verified: {completed_count} completed, {pending_count} pending")
        
        # Step 10: Delete one task
        print("\n=== Step 9: Deleting a task ===")
        response = api_client.delete(f'/api/tasks/{task_ids[2]}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        print(f"✓ Task deleted")
        
        # Step 11: Verify task was deleted
        response = api_client.get(f'/api/users/{user_id}/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        print(f"✓ User now has {len(response.data)} tasks")
        
        # Step 12: Delete the user (cascade delete should remove remaining tasks)
        print("\n=== Step 10: Deleting user ===")
        response = api_client.delete(f'/api/users/{user_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        print(f"✓ User deleted")
        
        # Step 13: Verify user and their tasks are gone
        response = api_client.get(f'/api/users/{user_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = api_client.get(f'/api/tasks/{task_ids[0]}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        print("\n=== ✓ E2E Test completed successfully! ===")


@pytest.mark.e2e
@pytest.mark.django_db
class TestMultiUserScenario:
    """
    Test scenario with multiple users managing their own tasks.
    """

    def test_multiple_users_with_separate_tasks(self, api_client):
        """Test that tasks are properly isolated between users."""
        
        # Create two users
        user1_data = {'name': 'Alice', 'email': 'alice@example.com'}
        user2_data = {'name': 'Bob', 'email': 'bob@example.com'}
        
        response1 = api_client.post('/api/users/', user1_data, format='json')
        response2 = api_client.post('/api/users/', user2_data, format='json')
        
        user1_id = response1.data['id']
        user2_id = response2.data['id']
        
        # Create tasks for user 1
        for i in range(3):
            api_client.post('/api/tasks/', {
                'title': f'Alice Task {i+1}',
                'user': user1_id
            }, format='json')
        
        # Create tasks for user 2
        for i in range(2):
            api_client.post('/api/tasks/', {
                'title': f'Bob Task {i+1}',
                'user': user2_id
            }, format='json')
        
        # Verify each user has only their tasks
        response1 = api_client.get(f'/api/users/{user1_id}/tasks/')
        response2 = api_client.get(f'/api/users/{user2_id}/tasks/')
        
        assert len(response1.data) == 3
        assert len(response2.data) == 2
        
        # Verify task ownership
        assert all('Alice' in task['title'] for task in response1.data)
        assert all('Bob' in task['title'] for task in response2.data)
        
        print("\n✓ Multiple users scenario completed successfully!")