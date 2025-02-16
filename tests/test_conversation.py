import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Conversation, AuditLog
from app.database import init_db  # Import the init_db function

# client = TestClient(app)

@pytest.fixture
async def clear_db():
    """
    Async fixture that truncates collections after each test.
    """
    # Initialize the database
    # await init_db()
    # Setup part goes here if needed
    yield
    # Teardown (run async code directly)
    await Conversation.find().delete()
    await AuditLog.find().delete()


def test_list_conversations(clear_db):
    """
    Test listing conversations returns an empty list initially,
    then one after creation. Empty list test requires an empty database.
    """
    # Initially empty
    with TestClient(app) as client:
        response = client.get("/conversations/")
        assert response.status_code == 200
        assert response.json() == []

        # Create one
        create_resp = client.post("/conversations/", json={"title": "Conv1"})
        assert create_resp.status_code == 201

        # Now list again
        response = client.get("/conversations/")
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Conv1"


def test_create_conversation(clear_db):
    """
    Test creating a conversation with a given title.
    """
    with TestClient(app) as client:
        response = client.post("/conversations/", json={"title": "Test Conversation"})
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Conversation"
        assert data["messages"] == []
        # Also check created_at, updated_at existence
        assert "created_at" in data
        assert "updated_at" in data


def test_get_conversation(clear_db):
    """
    Test getting a single conversation by ID.
    """
    with TestClient(app) as client:
        create_resp = client.post("/conversations/", json={"title": "Conv2"})
        conv_id = create_resp.json()["id"]

        # Retrieve
        get_resp = client.get(f"/conversations/{conv_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == conv_id
        assert data["title"] == "Conv2"

        # Non-existent
        bad_resp = client.get("/conversations/bad_id")
        assert bad_resp.status_code == 404

def test_update_conversation(clear_db):
    """
    Test updating the conversation title.
    """
    with TestClient(app) as client:
        # Create
        create_resp = client.post("/conversations/", json={"title": "Old Title"})
        conv_id = create_resp.json()["id"]

        # Update
        update_resp = client.put(f"/conversations/{conv_id}", json={"title": "New Title"})
        assert update_resp.status_code == 200
        updated_data = update_resp.json()
        assert updated_data["title"] == "New Title"

        # Check invalid ID
        invalid_resp = client.put("/conversations/bad_id", json={"title": "Doesn't matter"})
        assert invalid_resp.status_code == 404


def test_delete_conversation(clear_db):
    """
    Test deleting a conversation.
    """
    with TestClient(app) as client:
        # Create
        create_resp = client.post("/conversations/", json={"title": "ToDelete"})
        conv_id = create_resp.json()["id"]

        # Delete
        del_resp = client.delete(f"/conversations/{conv_id}")
        assert del_resp.status_code == 204

        # Try get
        get_resp = client.get(f"/conversations/{conv_id}")
        assert get_resp.status_code == 404

        # Try delete nonexistent
        invalid_resp = client.delete("/conversations/bad_id")
        assert invalid_resp.status_code == 404

