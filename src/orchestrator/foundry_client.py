from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

class FoundryClient:
    def __init__(self, endpoint: str):
        self.client = AIProjectClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential()
        )

    def run_agent_task(self, agent_id: str, prompt: str):
        thread = self.client.agents.threads.create()
        self.client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        run = self.client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent_id,
        )
        return run
