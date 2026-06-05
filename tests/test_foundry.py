import sys
import types
import json

import pytest

from src.orchestrator.client import LLMAdapter, ProviderConfigurationError


def test_unsupported_provider_raises_clear_error():
    with pytest.raises(ValueError, match="Unsupported LLM provider: not_real"):
        LLMAdapter(provider="not_real")


def test_foundry_agent_requires_endpoint_and_agent_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AZURE_AI_PROJECT_ENDPOINT", raising=False)
    monkeypatch.delenv("FOUNDRY_AGENT_NAME", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    with pytest.raises(ProviderConfigurationError, match="AZURE_AI_PROJECT_ENDPOINT"):
        LLMAdapter(provider="foundry_agent", load_env=False)


def test_foundry_agent_requires_agent_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://example.invalid")
    monkeypatch.delenv("FOUNDRY_AGENT_NAME", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    with pytest.raises(ProviderConfigurationError, match="FOUNDRY_AGENT_NAME"):
        LLMAdapter(provider="foundry_agent", load_env=False)


def test_foundry_agent_uses_project_openai_agent_reference(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            captured["raise_for_status"] = True

        def json(self):
            return {"output_text": "agent-ok"}

    class FakeProjectClient:
        def __init__(self, **kwargs):
            captured["project_client"] = kwargs

        def send_request(self, request):
            captured["request"] = request
            return FakeResponse()

    fake_projects = types.ModuleType("azure.ai.projects")
    fake_projects.AIProjectClient = FakeProjectClient
    monkeypatch.setitem(sys.modules, "azure.ai.projects", fake_projects)
    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "physics-agent")
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "2")
    monkeypatch.setenv("FOUNDRY_AGENT_API_VERSION", "2025-05-01-preview")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    adapter = LLMAdapter(provider="foundry_agent", load_env=False)
    response = adapter.generate_text(
        "Return JSON.",
        system_instruction="Use schema.",
        model="gpt-4.1",
    )

    assert response == "agent-ok"
    assert captured["project_client"]["endpoint"] == "https://example.invalid"
    assert captured["project_client"]["allow_preview"] is True
    assert captured["raise_for_status"] is True
    request = captured["request"]
    assert request.method == "POST"
    assert request.url == (
        "https://example.invalid/agents/physics-agent/"
        "endpoint/protocols/openai/responses?api-version=2025-05-01-preview"
    )
    assert request.query == {"api-version": "2025-05-01-preview"}
    body = json.loads(request.content)
    assert body["input"].startswith("Use schema.")
    assert "model" not in body


def test_foundry_agent_quotes_agent_name_in_project_endpoint(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"output_text": "agent-ok"}

    class FakeProjectClient:
        def __init__(self, **kwargs):
            pass

        def send_request(self, request):
            captured["url"] = request.url
            return FakeResponse()

    fake_projects = types.ModuleType("azure.ai.projects")
    fake_projects.AIProjectClient = FakeProjectClient
    monkeypatch.setitem(sys.modules, "azure.ai.projects", fake_projects)
    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://example.invalid/root/")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "physics agent/v1")
    monkeypatch.delenv("FOUNDRY_AGENT_VERSION", raising=False)

    adapter = LLMAdapter(provider="foundry_agent", load_env=False)

    assert adapter.generate_text("Return text.") == "agent-ok"
    assert captured["url"] == (
        "https://example.invalid/root/agents/physics%20agent%2Fv1/"
        "endpoint/protocols/openai/responses?api-version=v1"
    )


def test_foundry_agent_extracts_structured_response_text(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "output": [
                    {"content": [{"text": "first"}, {"text": "second"}]}
                ]
            }

    class FakeProjectClient:
        def __init__(self, **kwargs):
            captured["project_client"] = kwargs

        def send_request(self, request):
            captured["request"] = request
            return FakeResponse()

    fake_projects = types.ModuleType("azure.ai.projects")
    fake_projects.AIProjectClient = FakeProjectClient
    monkeypatch.setitem(sys.modules, "azure.ai.projects", fake_projects)
    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "physics-agent")
    monkeypatch.delenv("FOUNDRY_AGENT_VERSION", raising=False)

    adapter = LLMAdapter(provider="foundry_agent", load_env=False)

    assert adapter.generate_text("Return text.") == "first\nsecond"
    assert captured["project_client"]["allow_preview"] is True
    assert captured["request"].query == {"api-version": "v1"}
    assert json.loads(captured["request"].content) == {"input": "Return text."}


def test_foundry_agent_rejects_empty_api_version(monkeypatch):
    fake_projects = types.ModuleType("azure.ai.projects")
    fake_projects.AIProjectClient = object
    monkeypatch.setitem(sys.modules, "azure.ai.projects", fake_projects)
    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "physics-agent")
    monkeypatch.setenv("FOUNDRY_AGENT_API_VERSION", " ")

    with pytest.raises(ProviderConfigurationError, match="FOUNDRY_AGENT_API_VERSION"):
        LLMAdapter(provider="foundry_agent", load_env=False)


def test_foundry_agent_error_is_sanitized(monkeypatch):
    class FakeProjectClient:
        def __init__(self, **kwargs):
            pass

        def send_request(self, request):
            raise RuntimeError("Authorization: Bearer secret-token-value")

    fake_projects = types.ModuleType("azure.ai.projects")
    fake_projects.AIProjectClient = FakeProjectClient
    monkeypatch.setitem(sys.modules, "azure.ai.projects", fake_projects)
    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "physics-agent")

    adapter = LLMAdapter(provider="foundry_agent", load_env=False)

    with pytest.raises(RuntimeError) as exc_info:
        adapter.generate_text("Return text.")

    message = str(exc_info.value)
    assert "Bearer <redacted>" in message
    assert "secret-token-value" not in message


def test_env_file_is_loaded_without_printing_secret(tmp_path, monkeypatch, capsys):
    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.generativeai")
    captured = {}

    def configure(api_key):
        captured["api_key"] = api_key

    fake_genai.configure = configure
    fake_google.generativeai = fake_genai

    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "GEMINI_API_KEY=secret_from_env_file\n",
        encoding="utf-8",
    )

    adapter = LLMAdapter(provider="gemini", load_env=True, env_override=True)

    assert adapter.provider == "gemini"
    assert captured["api_key"] == "secret_from_env_file"

    output = capsys.readouterr()
    assert "secret_from_env_file" not in output.out
    assert "secret_from_env_file" not in output.err
