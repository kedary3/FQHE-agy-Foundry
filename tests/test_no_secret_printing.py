import os
import subprocess


def test_test_cli_does_not_print_secret_values(monkeypatch):
    fake_secret_values = {
        "AZURE_FOUNDRY_API_KEY": "secret-foundry-key-value",
        "GITHUB_TOKEN": "secret-github-token-value",
        "OPENAI_API_KEY": "secret-openai-key-value",
    }
    for name, value in fake_secret_values.items():
        monkeypatch.setenv(name, value)

    env = os.environ.copy()
    result = subprocess.run(
        [
            "python3",
            "-m",
            "src.orchestrator.cli",
            "--mode",
            "test",
            "--objective",
            "Check safe CLI output.",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    combined = result.stdout + result.stderr
    assert result.returncode == 0
    for value in fake_secret_values.values():
        assert value not in combined
