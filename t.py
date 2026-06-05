from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

endpoint = "https://kedary5-2236-resource.services.ai.azure.com/api/projects/kedary5-2236"
agent_id = "asst_6OcLkZOdBDp6Losa0xudg2B8"

client = AgentsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

agent = client.get_agent(agent_id)

print("agent id:", getattr(agent, "id", None))
print("agent name:", getattr(agent, "name", None))
print("agent model:", getattr(agent, "model", None))

print("\nPossible fields:")
for field in [
    "id",
    "name",
    "model",
    "instructions",
    "tools",
    "metadata",
    "created_at",
]:
    print(f"{field}:", getattr(agent, field, None))

print("\nRaw object:")
print(agent)

if hasattr(agent, "as_dict"):
    print("\nRaw dict:")
    print(agent.as_dict())