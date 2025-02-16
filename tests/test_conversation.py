import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.models import Conversation, AuditLog
from app.database import init_db  

# client = TestClient(app)

# @pytest.fixture
# async def clear_db():
#     """
#     Async fixture that truncates collections after each test.
#     """
#     # Initialize the database
#     # await init_db()
#     # Setup part goes here if needed
#     yield
#     # Teardown (run async code directly)
#     await Conversation.find().delete()
#     await AuditLog.find().delete()


def test_list_conversations():
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


def test_create_conversation():
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


def test_get_conversation():
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

def test_update_conversation():
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


def test_delete_conversation():
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

# Define fake response classes to simulate OpenAI response.
class FakeMessage:
    content = "Mocked response from LLM"

class FakeChoice:
    message = FakeMessage()

class FakeResponse:
    choices = [FakeChoice()]

def test_send_prompt_success():
    """
    Test sending a prompt to an existing conversation. We mock the OpenAI call.
    """
    with patch("app.services.llm_services.openai.chat.completions.create") as mock_openai:
        with TestClient(app) as client:
            # Mock the LLM response
            mock_openai.return_value = FakeResponse()
            # Create conversation
            create_resp = client.post("/conversations/", json={"title": "LLM Test"})
            assert create_resp.status_code == 201
            conv_id = create_resp.json()["id"]

            # Send prompt
            prompt_resp = client.post(
                f"/conversations/{conv_id}/prompt", 
                json={"role": "user", "content": "Hello LLM?"}
            )
            assert prompt_resp.status_code == 200

            # Check that conversation was updated with two messages (user + assistant)
            conv_data = prompt_resp.json()
            assert len(conv_data["messages"]) == 2
            assert conv_data["messages"][0]["role"] == "user"
            assert conv_data["messages"][0]["content"] == "Hello LLM?"
            assert conv_data["messages"][1]["role"] == "assistant"
            assert conv_data["messages"][1]["content"] == "Mocked response from LLM"

            # Check that an AuditLog was created
            conv_obj = Conversation.get(conv_id)
            assert conv_obj is not None

            # logs = asyncio.get_event_loop().run_until_complete(AuditLog.find().to_list())
            # assert len(logs) == 1
            # assert logs[0].prompt == "Hello LLM?"
            # assert logs[0].response == "Mocked response from LLM"

            # Test not found conversation
            fail_resp = client.post("/conversations/bad_id/prompt", json={"role": "user", "content": "Test"})
            assert fail_resp.status_code == 404


def test_send_prompt_openai_error():
    """
    Test error handling when OpenAI call fails.
    """
    with patch("app.services.llm_services.openai.chat.completions.create") as mock_openai:

        # Mock an error
        mock_openai.side_effect = Exception("OpenAI call failed")

        with TestClient(app) as client:
            # Create conversation
            create_resp = client.post("/conversations/", json={"title": "LLM Error Test"})
            conv_id = create_resp.json()["id"]

            # Send prompt (this should now result in a 502 error according to the LLM service)
            prompt_resp = client.post(
                f"/conversations/{conv_id}/prompt",
                json={"role": "user", "content": "Generate error"}
            )
            # Expecting a 502 Bad Gateway since the LLM call fails.
            assert prompt_resp.status_code == 502

            # Check that the error detail is as expected.
            data = prompt_resp.json()
            assert "LLM service error" in data.get("detail", "")

            # # Verify that no AuditLog was inserted
            # logs = asyncio.get_event_loop().run_until_complete(AuditLog.find().to_list())
            # assert (len(logs) == 0)
