import sys
import types

import pytest

from src.orchestrator.client import LLMAdapter, ProviderConfigurationError


def test_unsupported_provider_raises_clear_error():
    with pytest.raises(ValueError, match="Unsupported LLM provider: not_real"):
        LLMAdapter(provider="not_real")


def test_foundry_agent_requires_endpoint_and_agent_id(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AZURE_AI_PROJECT_ENDPOINT", raising=False)
    monkeypatch.delenv("FOUNDRY_AGENT_ID", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    with pytest.raises(ProviderConfigurationError, match="AZURE_AI_PROJECT_ENDPOINT"):
        LLMAdapter(provider="foundry_agent", load_env=False)


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