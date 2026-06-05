from azure.identity import DefaultAzureCredential
from azure.core.rest import HttpRequest
from azure.ai.projects import AIProjectClient
client = AIProjectClient(
    endpoint='https://kedary5-2236-resource.services.ai.azure.com/api/projects/kedary5-2236',
    credential=DefaultAzureCredential(),
)
for ver in ["2024-05-01-preview", "2024-07-01-preview", "2024-10-01-preview", "2024-12-01-preview"]:
    url = f"https://kedary5-2236-resource.services.ai.azure.com/api/projects/kedary5-2236/agents/FQHE-Agent/endpoint/protocols/openai/responses?api-version={ver}"
    req = HttpRequest("POST", url, headers={"Content-Type": "application/json"}, json={"input": "test"})
    try:
        resp = client.send_request(req)
        print(f"{ver}: {resp.status_code} - {resp.text()}")
    except Exception as e:
        print(f"{ver}: {e}")
