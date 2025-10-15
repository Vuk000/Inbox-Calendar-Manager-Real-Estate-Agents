"""
Tests for tasks API endpoints
"""
import pytest
from datetime import date, datetime
from app.models.task import Task, TaskType, TaskStatus


def test_create_task(client, auth_headers, test_user, db):
    """Test creating a new task"""
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Schedule property showing",
            "description": "Show 123 Main St to client",
            "task_type": "showing",
            "due_date": "2025-10-20",
            "priority": "high"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["title"] == "Schedule property showing"
    assert data["task_type"] == "showing"
    assert data["status"] == "todo"
    assert data["priority"] == "high"


def test_list_tasks(client, auth_headers, test_user, db):
    """Test listing tasks"""
    # Create test tasks
    task1 = Task(
        user_id=test_user.id,
        title="Task 1",
        task_type=TaskType.SHOWING,
        status=TaskStatus.TODO,
        priority="high"
    )
    task2 = Task(
        user_id=test_user.id,
        title="Task 2",
        task_type=TaskType.INSPECTION,
        status=TaskStatus.DONE,
        priority="medium",
        is_completed=True
    )
    
    db.add(task1)
    db.add(task2)
    db.commit()
    
    # List all tasks
    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_filter_tasks_by_status(client, auth_headers, test_user, db):
    """Test filtering tasks by status"""
    # Create tasks with different statuses
    task1 = Task(
        user_id=test_user.id,
        title="Todo Task",
        task_type=TaskType.SHOWING,
        status=TaskStatus.TODO,
        priority="medium"
    )
    task2 = Task(
        user_id=test_user.id,
        title="Done Task",
        task_type=TaskType.CALL,
        status=TaskStatus.DONE,
        priority="low",
        is_completed=True
    )
    
    db.add(task1)
    db.add(task2)
    db.commit()
    
    # Filter by TODO status
    response = client.get(
        "/api/v1/tasks?status=todo",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "todo"


def test_update_task_status(client, auth_headers, test_user, db):
    """Test updating task status"""
    # Create task
    task = Task(
        user_id=test_user.id,
        title="Update Test",
        task_type=TaskType.FOLLOW_UP,
        status=TaskStatus.TODO,
        priority="medium"
    )
    db.add(task)
    db.commit()
    
    # Update to done
    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers,
        json={"status": "done"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["is_completed"] == True
    assert data["completed_at"] is not None


def test_delete_task(client, auth_headers, test_user, db):
    """Test deleting a task"""
    # Create task
    task = Task(
        user_id=test_user.id,
        title="Delete Test",
        task_type=TaskType.GENERAL,
        status=TaskStatus.TODO,
        priority="low"
    )
    db.add(task)
    db.commit()
    task_id = task.id
    
    # Delete
    response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify deleted
    deleted_task = db.query(Task).filter(Task.id == task_id).first()
    assert deleted_task is None


def test_task_stats(client, auth_headers, test_user, db):
    """Test task statistics endpoint"""
    # Create various tasks
    tasks = [
        Task(user_id=test_user.id, title="T1", task_type=TaskType.SHOWING, status=TaskStatus.TODO, priority="high"),
        Task(user_id=test_user.id, title="T2", task_type=TaskType.INSPECTION, status=TaskStatus.IN_PROGRESS, priority="medium"),
        Task(user_id=test_user.id, title="T3", task_type=TaskType.CALL, status=TaskStatus.DONE, priority="low", is_completed=True),
    ]
    
    for task in tasks:
        db.add(task)
    db.commit()
    
    # Get stats
    response = client.get(
        "/api/v1/tasks/stats/summary",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 3
    assert data["todo"] == 1
    assert data["in_progress"] == 1
    assert data["done"] == 1

