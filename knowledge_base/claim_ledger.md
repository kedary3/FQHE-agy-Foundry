# claim_ledger

## 20260531-072603-production-6b984b3c

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "unknown-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Agent output missing required field(s): agent_name, agent_role, errors, mode, run_id, status, summary, task_id"
    },
    {
      "claim_id": "unknown-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Agent output missing required field(s): agent_name, agent_role, errors, mode, run_id, status, summary, task_id"
    },
    {
      "claim_id": "unknown-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Agent output missing required field(s): agent_name, agent_role, errors, mode, run_id, status, summary, task_id"
    },
    {
      "claim_id": "unknown-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Agent output missing required field(s): agent_name, agent_role, errors, mode, run_id, status, summary, task_id"
    },
    {
      "claim_id": "unknown-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Agent output missing required field(s): agent_name, agent_role, errors, mode, run_id, status, summary, task_id"
    },
    {
      "claim_id": "unknown-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Agent output missing required field(s): agent_name, agent_role, errors, mode, run_id, status, summary, task_id"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Return output matching the required agent schema."
  ]
}

## 20260601-043655-production-d7c2080e

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: Traceback (most recent call last):\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 36, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"<frozen runpy>\", line 198, in _run_module_as_main\n  File \"<frozen runpy>\", line 88, in _run_code\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/__main__.py\", line 30, in <module>\n    az_cli = get_default_cli()\n             ^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 955, in get_default_cli\n    return AzCli(cli_name='az',\n           ^^^^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 82, in __init__\n    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 50, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: Traceback (most recent call last):\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 36, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"<frozen runpy>\", line 198, in _run_module_as_main\n  File \"<frozen runpy>\", line 88, in _run_code\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/__main__.py\", line 30, in <module>\n    az_cli = get_default_cli()\n             ^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 955, in get_default_cli\n    return AzCli(cli_name='az',\n           ^^^^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 82, in __init__\n    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 50, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n"
    },
    {
      "claim_id": "production-03-numerics_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: Traceback (most recent call last):\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 36, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"<frozen runpy>\", line 198, in _run_module_as_main\n  File \"<frozen runpy>\", line 88, in _run_code\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/__main__.py\", line 30, in <module>\n    az_cli = get_default_cli()\n             ^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 955, in get_default_cli\n    return AzCli(cli_name='az',\n           ^^^^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 82, in __init__\n    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 50, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n"
    },
    {
      "claim_id": "production-04-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: Traceback (most recent call last):\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 36, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"<frozen runpy>\", line 198, in _run_module_as_main\n  File \"<frozen runpy>\", line 88, in _run_code\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/__main__.py\", line 30, in <module>\n    az_cli = get_default_cli()\n             ^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 955, in get_default_cli\n    return AzCli(cli_name='az',\n           ^^^^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 82, in __init__\n    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 50, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n"
    },
    {
      "claim_id": "production-05-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: Traceback (most recent call last):\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 36, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"<frozen runpy>\", line 198, in _run_module_as_main\n  File \"<frozen runpy>\", line 88, in _run_code\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/__main__.py\", line 30, in <module>\n    az_cli = get_default_cli()\n             ^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 955, in get_default_cli\n    return AzCli(cli_name='az',\n           ^^^^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 82, in __init__\n    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 50, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n"
    },
    {
      "claim_id": "production-06-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: Traceback (most recent call last):\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 36, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"<frozen runpy>\", line 198, in _run_module_as_main\n  File \"<frozen runpy>\", line 88, in _run_code\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/__main__.py\", line 30, in <module>\n    az_cli = get_default_cli()\n             ^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 955, in get_default_cli\n    return AzCli(cli_name='az',\n           ^^^^^^^^^^^^^^^^^^^^\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/__init__.py\", line 82, in __init__\n    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 50, in load\n    self.save()\n  File \"/opt/az/lib/python3.12/site-packages/azure/cli/core/_session.py\", line 54, in save\n    with open(self.filename, 'w', encoding=self._encoding) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nOSError: [Errno 30] Read-only file system: '/home/kedary3/.azure/az.sess'\n"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260601-043747-production-f75abacb

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x7709b8c8d060>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x7709b8c8cc70>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-03-numerics_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x7709b8c8dae0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-04-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x7709b8ce1f00>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-05-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x7709b8ce2ec0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-06-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x7709b8ce2680>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260601-044021-production-c89cc802

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x75edada50ac0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x75edada513f0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-03-numerics_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x75edada50eb0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-04-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x75edadab9d20>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-05-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x75edadaba500>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-06-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x75edadabace0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260601-044053-production-2ae2bdd8

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x77a11da5d0c0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x77a11da5d690>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-03-numerics_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x77a11da5ceb0>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-04-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x77a11daa5f30>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-05-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x77a11daa6710>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    },
    {
      "claim_id": "production-06-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: ChainedTokenCredential failed to retrieve a token from the included credentials.\nAttempted credentials:\n\tEnvironmentCredential: Authentication failed: <urllib3.connection.HTTPSConnection object at 0x77a11ebfcb80>: Failed to establish a new connection: [Errno -2] Name or service not known\nTo mitigate this issue, please refer to the troubleshooting guidelines here at https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot."
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260601-044258-production-bdf88956

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: (PermissionDenied) Principal does not have access to API/Operation.\nCode: PermissionDenied\nMessage: Principal does not have access to API/Operation."
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: (PermissionDenied) Principal does not have access to API/Operation.\nCode: PermissionDenied\nMessage: Principal does not have access to API/Operation."
    },
    {
      "claim_id": "production-03-numerics_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: (PermissionDenied) The principal `72041528-808c-43fd-9506-56fed3e4feae` lacks the required data action `Microsoft.CognitiveServices/accounts/AIServices/agents/read` to perform `POST /api/projects/{projectName}/threads` operation. For instructions on granting the necessary permissions, see https://aka.ms/FoundryPermissions.\nCode: PermissionDenied\nMessage: The principal `72041528-808c-43fd-9506-56fed3e4feae` lacks the required data action `Microsoft.CognitiveServices/accounts/AIServices/agents/read` to perform `POST /api/projects/{projectName}/threads` operation. For instructions on granting the necessary permissions, see https://aka.ms/FoundryPermissions."
    },
    {
      "claim_id": "production-04-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: (PermissionDenied) Principal does not have access to API/Operation.\nCode: PermissionDenied\nMessage: Principal does not have access to API/Operation."
    },
    {
      "claim_id": "production-05-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: (PermissionDenied) Principal does not have access to API/Operation.\nCode: PermissionDenied\nMessage: Principal does not have access to API/Operation."
    },
    {
      "claim_id": "production-06-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "ClientAuthenticationError: (PermissionDenied) Principal does not have access to API/Operation.\nCode: PermissionDenied\nMessage: Principal does not have access to API/Operation."
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-050357-production-949aa3bb

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-055701-production-b800073d

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent run failed: {'code': 'invalid_engine_error', 'message': 'Failed to resolve model info for: gpt-4.1'}"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-083214-production-7e094669

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-083510-production-61b90de2

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-084305-production-7d7e4131

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-084644-production-5514e418

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-084718-production-b10368ea

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): Error code: 404 - {'error': {'message': 'The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.', 'type': 'invalid_request_error', 'param': None, 'code': 'DeploymentNotFound'}}"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-085753-production-80cbd065

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-090524-production-09111159

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-090607-production-e62e9007

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) Missing required query parameter: api-version\nCode: BadRequest\nMessage: Missing required query parameter: api-version"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-090959-production-4e6577f0

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-091415-production-ca9f9105

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-091856-production-22c59ec3

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=unspecified): (BadRequest) API version not supported\nCode: BadRequest\nMessage: API version not supported"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-101227-production-237c788b

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=2): (DeploymentNotFound) The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.\nCode: DeploymentNotFound\nMessage: The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again."
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=2): (DeploymentNotFound) The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.\nCode: DeploymentNotFound\nMessage: The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again."
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=2): (DeploymentNotFound) The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.\nCode: DeploymentNotFound\nMessage: The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again."
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=2): (DeploymentNotFound) The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.\nCode: DeploymentNotFound\nMessage: The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again."
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Subagent execution raised an exception.",
      "reason": "RuntimeError: Foundry Agent response failed (provider=foundry_agent, agent_name=FQHE-Agent, agent_version=2): (DeploymentNotFound) The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again.\nCode: DeploymentNotFound\nMessage: The API deployment for this resource does not exist. If you created the deployment within the last 5 minutes, please wait a moment and try again."
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Inspect exception and rerun the failed task."
  ]
}

## 20260605-102544-production-d11832f1

{
  "accepted_claims": [],
  "rejected_claims": [
    {
      "claim_id": "production-01-literature_agent-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Invalid agent status: partial_success"
    },
    {
      "claim_id": "production-02-theory_agent-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Invalid agent status: completed"
    },
    {
      "claim_id": "production-03-falsification_agent-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Invalid agent status: completed"
    },
    {
      "claim_id": "production-04-experiment_bridge_agent-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Claim missing required field: claim_id"
    },
    {
      "claim_id": "production-05-knowledge_curator_agent-failed-output",
      "text": "Output rejected by Director schema validation.",
      "reason": "Claim missing required field: text"
    }
  ],
  "deferred_claims": [],
  "unresolved_assumptions": [],
  "proposed_next_tests": [
    "Return output matching the required agent schema."
  ]
}
