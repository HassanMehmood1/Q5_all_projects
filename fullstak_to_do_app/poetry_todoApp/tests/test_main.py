from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
from poetry_todoapp.main import app, get_session
from poetry_todoapp import settings
import pytest
import os


# Fixture to set up the test database
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    os.environ["TESTING"] = "1"  # Indicate we are in testing mode
    engine = create_engine(str(settings.TEST_DATABASE_URL))
    SQLModel.metadata.create_all(engine)  # Create all tables
    yield  # Run the tests
    SQLModel.metadata.drop_all(engine)  # Cleanup: Drop all tables
    del os.environ["TESTING"]

# Override get_session for tests to use the test database
@pytest.fixture
def session_override():
    engine = create_engine(str(settings.TEST_DATABASE_URL))
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session_override):
    # Use TestClient to create a testing instance of your FastAPI app
    app.dependency_overrides[get_session] = lambda: session_override
    with TestClient(app) as client:
        yield client


def test_create_task(client):
    response = client.post("/tasks/", json={"title": "New Task", "description": "A new task description"})
    assert response.status_code == 200
    task = response.json()
    assert task['title'] == "New Task"
    assert "id" in task

def test_read_tasks(client, test_task):
    response = client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert any(task['id'] == test_task['id'] for task in tasks)

def test_update_task(client, test_task):
    task_id = test_task['id']
    updated_title = "Updated Task"
    response = client.patch(f"/tasks/{task_id}", json={"title": updated_title})
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task['title'] == updated_title

def test_delete_task(client, test_task):
    task_id = test_task['id']
    # Delete the task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    # Verify the task is deleted by attempting to fetch it
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404 or response.status_code == 405

@pytest.fixture
def test_task(client):
    # Create a test task using the client
    response = client.post("/tasks/", json={"title": "Test Task", "description": "A test task description"})
    assert response.status_code == 200
    task = response.json()
    yield task
    # Cleanup: delete the test task after the test is done
    client.delete(f"/tasks/{task['id']}")

