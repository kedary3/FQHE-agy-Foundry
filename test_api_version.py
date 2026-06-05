from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import inspect
print("AIProjectClient constructor:")
print(inspect.signature(AIProjectClient.__init__))
try:
    client = AIProjectClient(
        endpoint='https://kedary5-2236-resource.services.ai.azure.com/api/projects/kedary5-2236',
        credential=DefaultAzureCredential(),
        api_version='2024-05-01-preview'
    )
    print("Successfully instantiated with api_version")
except Exception as e:
    print(f"Error: {e}")
