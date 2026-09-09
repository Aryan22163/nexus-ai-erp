from unittest.mock import AsyncMock, patch
import uuid
import pytest
from app.ai.agents.orchestrator import AICopilotOrchestrator
from app.ai.llm_client import OpenSourceLLMClient
from app.schemas.ai import AICopilotRequest


@pytest.mark.asyncio
async def test_open_source_llm_client_instantiation():
    client = OpenSourceLLMClient(base_url="http://localhost:11434/v1", model="llama3.1")
    assert client.model == "llama3.1"
    assert client.base_url == "http://localhost:11434/v1"
    available = await client.is_available()
    assert isinstance(available, bool)


@pytest.mark.asyncio
async def test_orchestrator_open_source_llm_graceful_fallback():
    mock_session = AsyncMock()
    orchestrator = AICopilotOrchestrator(
        session=mock_session,
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        user_permissions=["ai.copilot.query"],
    )
    req = AICopilotRequest(prompt="What are standard working capital best practices in 2026?")
    resp = await orchestrator.process_prompt(req)
    assert resp.intent == "OPEN_SOURCE_LLM"
    assert "NEXUS AI" in resp.reply or "llama3.1" in resp.reply


@pytest.mark.asyncio
async def test_orchestrator_open_source_llm_generation():
    mock_session = AsyncMock()
    orchestrator = AICopilotOrchestrator(
        session=mock_session,
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        user_permissions=["ai.copilot.query"],
    )
    with patch("app.ai.agents.orchestrator.open_source_llm.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Maintain a current ratio between 1.5 and 2.0 to ensure liquidity."
        req = AICopilotRequest(prompt="Explain supply chain best practices in modern manufacturing.")
        resp = await orchestrator.process_prompt(req)
        assert resp.intent == "OPEN_SOURCE_LLM"
        assert "Maintain a current ratio" in resp.reply
        assert "Open-Source" in resp.reply

