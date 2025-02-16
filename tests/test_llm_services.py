import pytest
import re
from fastapi import HTTPException
from app.services.llm_services import get_llm_response, mask_sensitive_info, openai
from app.models import AuditLog


def test_mask_sensitive_info():
    test_text = (
        "Contact me at user@example.com, call me at +65 91234567. "
        "My NRIC is S1234567D and postal code is 123456. "
        "Visit my office at Blk 123 Ang Mo Kio Ave 3 or 123 Orchard Road."
    )
    masked = mask_sensitive_info(test_text)
    # Check that email is masked
    assert "[MASKED_EMAIL]" in masked
    # Check that phone number is masked
    assert "[MASKED_PHONE]" in masked
    # Check that NRIC is masked
    assert "[MASKED_NRIC]" in masked
    # Check that postal code is masked
    assert "[MASKED_POSTAL]" in masked
    # Check that addresses are masked (at least one occurrence)
    assert "[MASKED_ADDRESS]" in masked

    # Optionally, verify that the sensitive strings are no longer present.
    assert "user@example.com" not in masked
    assert "+65 91234567" not in masked
    assert "S1234567D" not in masked
    assert "123456" not in masked
    assert "Blk 123 Ang Mo Kio Ave 3" not in masked
    assert "123 Orchard Road" not in masked


# Define fake response classes to simulate OpenAI response.
class FakeMessage:
    content = "This is a reply with email: reply@example.com"

class FakeChoice:
    message = FakeMessage()

class FakeResponse:
    choices = [FakeChoice()]

@pytest.mark.asyncio
async def test_get_llm_response_success(monkeypatch):
    """
    Test that get_llm_response returns the expected reply and that an AuditLog is created
    with masked sensitive information.
    """
    # --- Patch the OpenAI completions call ---
    def fake_create(*args, **kwargs):
        return FakeResponse()
    monkeypatch.setattr(openai.chat.completions, "create", fake_create)

    # --- Patch AuditLog.insert to capture the inserted values ---
    captured_audit = {}

    async def fake_insert(self):
        # Capture the values from the AuditLog instance
        captured_audit["conversation_id"] = self.conversation_id
        captured_audit["prompt"] = self.prompt
        captured_audit["response"] = self.response

    monkeypatch.setattr(AuditLog, "insert", fake_insert)

    # Prepare a sample context with sensitive info in the user prompt.
    context_messages = [
        {"role": "user", "content": "Hello, my email is user@example.com"}
    ]
    convo_id = "test-convo-1"

    # Call the function
    reply = await get_llm_response(context_messages, convo_id)

    # Check that the reply is as expected from our fake response.
    assert reply == "This is a reply with email: reply@example.com"

    # Verify that the audit log was inserted with masked values.
    assert captured_audit.get("conversation_id") == convo_id

    # The prompt originally was built from the user message.
    # It should have been masked so that "user@example.com" is replaced.
    assert "[MASKED_EMAIL]" in captured_audit.get("prompt", "")
    assert "user@example.com" not in captured_audit.get("prompt", "")

    # Similarly, the LLM reply should have the email masked.
    assert "[MASKED_EMAIL]" in captured_audit.get("response", "")
    assert "reply@example.com" not in captured_audit.get("response", "")

@pytest.mark.asyncio
async def test_get_llm_response_failure(monkeypatch):
    """
    Test that if the OpenAI call fails, get_llm_response raises an HTTPException with status code 502.
    """
    # Patch openai.chat.completions.create to raise an Exception.
    def fake_create_failure(*args, **kwargs):
        raise Exception("Fake error")
    monkeypatch.setattr(openai.chat.completions, "create", fake_create_failure)

    context_messages = [{"role": "user", "content": "Test message"}]
    convo_id = "test-failure"

    with pytest.raises(HTTPException) as exc_info:
        await get_llm_response(context_messages, convo_id)

    assert exc_info.value.status_code == 502
    assert "LLM service error" in exc_info.value.detail