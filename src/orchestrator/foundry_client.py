# src/orchestrator/foundry_client.py

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.core.rest import HttpRequest
import os
from urllib.parse import quote

load_dotenv()


class FoundryClient:
    def __init__(self, endpoint: str = None):
        from .client import _foundry_credential, _require_env

        self.endpoint = endpoint or _require_env("AZURE_AI_PROJECT_ENDPOINT")
        self.agent_name = _require_env("FOUNDRY_AGENT_NAME")
        self.endpoint = self.endpoint.rstrip("/")
        self.api_version = os.environ.get("FOUNDRY_AGENT_API_VERSION", "v1").strip()
        if not self.api_version:
            raise ValueError("FOUNDRY_AGENT_API_VERSION must not be empty.")
        self.project = AIProjectClient(
            endpoint=self.endpoint,
            credential=_foundry_credential(),
            allow_preview=True,
        )

    def run_agent(self, content: str, agent_version: str | None = None):
        request = {"input": content}
        if agent_version:
            request["agent_reference"] = {
                "name": self.agent_name,
                "type": "agent_reference",
                "version": agent_version,
            }
        response = self.project.send_request(
            HttpRequest(
                "POST",
                self._responses_url(),
                params={"api-version": self.api_version},
                headers={"Content-Type": "application/json"},
                json=request,
            )
        )
        response.raise_for_status()
        return response

    def _responses_url(self) -> str:
        agent_name = quote(self.agent_name, safe="")
        return (
            f"{self.endpoint}/agents/{agent_name}/"
            "endpoint/protocols/openai/responses"
        )
