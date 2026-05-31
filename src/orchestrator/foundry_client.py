# src/orchestrator/foundry_client.py

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

class FoundryClient:
    def __init__(self, endpoint: str = None):
        from .client import _require_env

        self.endpoint = endpoint or _require_env("AZURE_AI_PROJECT_ENDPOINT")
        self.project = AIProjectClient(
            endpoint=self.endpoint,
            credential=DefaultAzureCredential(),
        )

    def create_thread(self):
        return self.project.agents.threads.create()

    def send_message(self, thread_id: str, content: str):
        return self.project.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
        )

    def run_agent(self, agent_id: str, thread_id: str):
        return self.project.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent_id,
        )
