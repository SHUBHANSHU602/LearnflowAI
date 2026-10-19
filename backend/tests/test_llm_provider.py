import asyncio
import httpx
import pytest

from backend.llm_provider import (
    ModelProvider, OpenAICompatibleProvider, ProviderConfig, ProviderError
)

CONFIG = ProviderConfig(endpoint="https://provider.example/v1/chat/completions",
                        model="test-model", api_key="super-secret")


def test_provider_uses_evidence_and_auth():
    async def mock(request):
        assert request.headers["authorization"] == "Bearer super-secret"
        payload = __import__("json").loads(request.content)
        assert "[E1] Lecture about caching" in payload["messages"][1]["content"]
        assert payload["temperature"] == 0
        return httpx.Response(200, json={"choices": [{"message": {"content": "Caching stores data."}}]})
    provider = OpenAICompatibleProvider(CONFIG, transport=httpx.MockTransport(mock))
    assert asyncio.run(provider.answer("What is caching?", ["Lecture about caching"])) == "Caching stores data."


def test_no_evidence_never_calls_provider():
    provider = OpenAICompatibleProvider(CONFIG)
    with pytest.raises(ProviderError, match="approved evidence"):
        asyncio.run(provider.answer("Anything?", []))


def test_no_secrets_in_provider_errors():
    async def mock(request):
        return httpx.Response(401, json={"detail": "super-secret"})
    provider = OpenAICompatibleProvider(CONFIG, transport=httpx.MockTransport(mock))
    with pytest.raises(ProviderError) as error:
        asyncio.run(provider.answer("Q?", ["Evidence"]))
    assert "super-secret" not in str(error.value)


def test_provider_retries_transient_error():
    calls = 0
    async def mock(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"choices":[{"message":{"content":"Retry worked"}}]})
    provider = OpenAICompatibleProvider(CONFIG, transport=httpx.MockTransport(mock))
    assert asyncio.run(provider.answer("Q", ["Source"])) == "Retry worked"
    assert calls == 2


def test_provider_requires_secure_config(monkeypatch):
    monkeypatch.setenv("LEARNFLOW_MODEL_ENDPOINT", "http://local/ai")
    monkeypatch.setenv("LEARNFLOW_MODEL_API_KEY", "key")
    monkeypatch.setenv("LEARNFLOW_MODEL_NAME", "model")
    with pytest.raises(ProviderError, match="HTTPS"):
        ProviderConfig.from_env()


def test_provider_rejects_malformed_success_payload():
    async def mock(request):
        return httpx.Response(200, json={"choices": []})
    provider = OpenAICompatibleProvider(CONFIG, transport=httpx.MockTransport(mock))
    with pytest.raises(ProviderError, match="invalid response"):
        asyncio.run(provider.answer("Explain this", ["Grounded source text"]))


def test_provider_config_requires_all_credentials(monkeypatch):
    monkeypatch.delenv("LEARNFLOW_MODEL_API_KEY", raising=False)
    monkeypatch.setenv("LEARNFLOW_MODEL_NAME", "test-model")
    monkeypatch.setenv("LEARNFLOW_MODEL_ENDPOINT", "https://provider.example/v1/chat/completions")
    with pytest.raises(ProviderError, match="not configured"):
        ProviderConfig.from_env()
