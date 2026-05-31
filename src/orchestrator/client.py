# File: src/orchestrator/client.py
"""LLM provider adapter for local and managed research agents."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

logger = logging.getLogger("orchestrator.client")


class ProviderConfigurationError(RuntimeError):
    """Raised when a provider is selected but required configuration is absent."""


def _load_environment(override: bool = False) -> None:
    """Load local `.env`.

    By default, explicit process environment variables are preserved.
    Tests may pass override=True when checking a temporary .env file.
    """
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=override)


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise ProviderConfigurationError(
            f"Missing required environment variable: {name}"
        )
    return value.strip()


def _first_env(names: Iterable[str]) -> str:
    for name in names:
        value = os.environ.get(name)
        if value is not None and value.strip():
            return value.strip()

    joined = " or ".join(names)
    raise ProviderConfigurationError(
        f"Missing required environment variable: {joined}"
    )


class LLMAdapter:
    """Thin adapter that returns plain generated text for supported providers."""

    SUPPORTED_PROVIDERS = {
        "gemini",
        "openai",
        "anthropic",
        "azure_openai",
        "foundry_agent",
    }

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        load_env: bool = False,
        env_override: bool = False,
    ) -> None:
        if load_env:
            _load_environment(override=env_override)

        self.provider = (provider or os.environ.get("LLM_PROVIDER", "gemini")).lower()
        self.api_key = api_key
        self.client = None
        self._agent_id = None

        if self.provider not in self.SUPPORTED_PROVIDERS:
            supported = ", ".join(sorted(self.SUPPORTED_PROVIDERS))
            raise ValueError(
                f"Unsupported LLM provider: {self.provider}. "
                f"Supported providers: {supported}"
            )

        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        elif self.provider == "azure_openai":
            self._init_azure_openai()
        elif self.provider == "foundry_agent":
            self._init_foundry_agent()

    def _init_gemini(self) -> None:
        api_key = self.api_key or _first_env(("GEMINI_API_KEY", "GOOGLE_API_KEY"))

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "Provider 'gemini' requires package 'google-generativeai'."
            ) from exc

        genai.configure(api_key=api_key)
        self.client = genai
        logger.info("Initialized Gemini provider.")

    def _init_openai(self) -> None:
        api_key = self.api_key or _require_env("OPENAI_API_KEY")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Provider 'openai' requires package 'openai'.") from exc

        self.client = OpenAI(api_key=api_key)
        logger.info("Initialized OpenAI provider.")

    def _init_anthropic(self) -> None:
        api_key = self.api_key or _require_env("ANTHROPIC_API_KEY")

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "Provider 'anthropic' requires package 'anthropic'."
            ) from exc

        self.client = Anthropic(api_key=api_key)
        logger.info("Initialized Anthropic provider.")

    def _init_azure_openai(self) -> None:
        api_key = self.api_key or _require_env("AZURE_OPENAI_API_KEY")
        endpoint = _require_env("AZURE_OPENAI_ENDPOINT")
        _require_env("AZURE_OPENAI_DEPLOYMENT")
        api_version = _require_env("AZURE_OPENAI_API_VERSION")

        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise ImportError(
                "Provider 'azure_openai' requires package 'openai'."
            ) from exc

        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )
        logger.info("Initialized Azure OpenAI provider.")

    def _init_foundry_agent(self) -> None:
        endpoint = _require_env("AZURE_AI_PROJECT_ENDPOINT")
        self._agent_id = _require_env("FOUNDRY_AGENT_ID")

        try:
            from azure.ai.agents import AgentsClient
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:
            raise ImportError(
                "Provider 'foundry_agent' requires packages "
                "'azure-ai-agents' and 'azure-identity'."
            ) from exc

        self.client = AgentsClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )
        logger.info("Initialized Foundry Agent provider.")

    def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
    ) -> str:
        """Generate text with the configured provider and return plain response text."""
        if self.provider == "gemini":
            selected_model = model or os.environ.get(
                "GEMINI_MODEL",
                "gemini-1.5-flash",
            )
            model_instance = self.client.GenerativeModel(
                model_name=selected_model,
                system_instruction=system_instruction,
            )
            response = model_instance.generate_content(prompt)
            return getattr(response, "text", "")

        if self.provider == "openai":
            selected_model = model or os.environ.get(
                "OPENAI_MODEL",
                "gpt-4o-mini",
            )
            messages = self._messages(prompt, system_instruction)
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
            )
            return response.choices[0].message.content or ""

        if self.provider == "anthropic":
            selected_model = model or os.environ.get(
                "ANTHROPIC_MODEL",
                "claude-3-5-sonnet-20241022",
            )
            kwargs = {"system": system_instruction} if system_instruction else {}
            response = self.client.messages.create(
                model=selected_model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.content[0].text

        if self.provider == "azure_openai":
            selected_deployment = model or os.environ.get("AZURE_OPENAI_DEPLOYMENT")
            messages = self._messages(prompt, system_instruction)
            response = self.client.chat.completions.create(
                model=selected_deployment,
                messages=messages,
            )
            return response.choices[0].message.content or ""

        if self.provider == "foundry_agent":
            return self._generate_foundry_agent_text(prompt, system_instruction)

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    @staticmethod
    def _messages(
        prompt: str,
        system_instruction: str | None,
    ) -> list[dict[str, str]]:
        messages = []

        if system_instruction:
            messages.append(
                {
                    "role": "system",
                    "content": system_instruction,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return messages

    def _generate_foundry_agent_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        content = prompt if not system_instruction else f"{system_instruction}\n\n{prompt}"

        agents = getattr(self.client, "agents", self.client)
        thread = agents.threads.create()

        agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=content,
        )

        run = agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=self._agent_id,
        )

        if getattr(run, "status", None) == "failed":
            error = getattr(run, "last_error", None)
            raise RuntimeError(f"Foundry Agent run failed: {error}")

        messages = agents.messages.list(thread_id=thread.id)

        for message in messages:
            if getattr(message, "role", None) != "assistant":
                continue

            text = self._extract_foundry_message_text(message)
            if text:
                return text

        return ""

    @staticmethod
    def _extract_foundry_message_text(message) -> str:
        parts = []

        for item in getattr(message, "content", []) or []:
            text_obj = getattr(item, "text", None)
            value = getattr(text_obj, "value", None)

            if value:
                parts.append(value)

        return "\n".join(parts)
