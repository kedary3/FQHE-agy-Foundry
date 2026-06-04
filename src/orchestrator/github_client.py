# File: src/orchestrator/github_client.py
"""GitHub API client adapter using PyGithub for task and PR automation."""

import os
import logging

logger = logging.getLogger("orchestrator.github")


class GitHubClient:
    def __init__(self, repo_name: str = None, token: str = None):
        """
        Initializes the GitHub client.

        Args:
            repo_name (str): The 'owner/repo' name. Defaults to RESEARCH_REPOSITORY or GITHUB_REPOSITORY env variables.
            token (str): The personal access token. Defaults to GITHUB_TOKEN env variable.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.repo_name = repo_name or os.environ.get("RESEARCH_REPOSITORY") or os.environ.get("GITHUB_REPOSITORY")
        self.github = None
        self.repo = None

        if not self.token:
            logger.warning("GITHUB_TOKEN is not set. GitHub operations will fail.")
            return

        if not self.repo_name:
            logger.warning("GitHub repository name is not configured. Specify RESEARCH_REPOSITORY (e.g., 'owner/repo').")
            return

        try:
            from github import Github
            self.github = Github(self.token)
            self.repo = self.github.get_repo(self.repo_name)
            logger.info(f"Successfully connected to GitHub repository: {self.repo_name}")
        except Exception as e:
            logger.error(f"Failed to connect to GitHub repository: {e}")
            raise

    def is_configured(self) -> bool:
        """Checks if the client is successfully connected to the repository."""
        return self.repo is not None

    def get_issues_by_label(self, label: str) -> list:
        """
        Fetch open issues containing a specific label.

        Args:
            label (str): The label to search for.

        Returns:
            list: List of PyGithub Issue objects.
        """
        if not self.is_configured():
            logger.error("GitHub client is not configured.")
            return []
        from github import GithubException
        try:
            issues = self.repo.get_issues(state="open", labels=[label])
            return list(issues)
        except GithubException as e:
            logger.error(f"Error fetching issues with label {label}: {e}")
            return []

    def get_open_issues(self, limit: int = 20) -> list:
        """
        Fetch recent open issues without mutating GitHub state.

        Args:
            limit (int): Maximum number of open issues to return.

        Returns:
            list: List of PyGithub Issue objects.
        """
        if not self.is_configured():
            logger.error("GitHub client is not configured.")
            return []
        from github import GithubException
        try:
            issues = self.repo.get_issues(state="open")
            return list(issues[:limit])
        except GithubException as e:
            logger.error(f"Error fetching open issues: {e}")
            return []

    def create_issue(self, title: str, body: str, labels: list = None) -> int:
        """
        Create a new GitHub issue.

        Args:
            title (str): Issue title.
            body (str): Issue description (markdown).
            labels (list): List of labels to apply.

        Returns:
            int: The new issue number, or -1 on failure.
        """
        if not self.is_configured():
            return -1
        from github import GithubException
        try:
            issue = self.repo.create_issue(title=title, body=body, labels=labels or [])
            logger.info(f"Created Issue #{issue.number}: '{title}'")
            return issue.number
        except GithubException as e:
            logger.error(f"Error creating issue: {e}")
            return -1

    def update_issue_labels(self, issue_number: int, labels: list):
        """
        Replace all labels on an issue.

        Args:
            issue_number (int): Issue identifier.
            labels (list): Complete list of new labels.
        """
        if not self.is_configured():
            return
        from github import GithubException
        try:
            issue = self.repo.get_issue(issue_number)
            issue.set_labels(*labels)
            logger.info(f"Updated Issue #{issue_number} labels to: {labels}")
        except GithubException as e:
            logger.error(f"Error updating labels for Issue #{issue_number}: {e}")

    def add_comment(self, issue_number: int, comment: str):
        """
        Leave a comment on a GitHub issue or Pull Request.

        Args:
            issue_number (int): Issue or PR identifier.
            comment (str): Comment body (markdown).
        """
        if not self.is_configured():
            return
        from github import GithubException
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            logger.info(f"Added comment on Issue/PR #{issue_number}")
        except GithubException as e:
            logger.error(f"Error leaving comment on Issue/PR #{issue_number}: {e}")

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "main") -> int:
        """
        Create a new Pull Request.

        Args:
            title (str): PR title.
            body (str): PR description.
            head_branch (str): Source branch name.
            base_branch (str): Target branch name.

        Returns:
            int: The new PR number, or -1 on failure.
        """
        if not self.is_configured():
            return -1
        from github import GithubException
        try:
            pr = self.repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
            logger.info(f"Successfully created PR #{pr.number}: '{title}' (from {head_branch} to {base_branch})")
            return pr.number
        except GithubException as e:
            logger.error(f"Error creating pull request: {e}")
            return -1

    def merge_pull_request(self, pr_number: int, commit_message: str = None) -> bool:
        """
        Merge an approved Pull Request.

        Args:
            pr_number (int): PR identifier.
            commit_message (str): Optional commit message.

        Returns:
            bool: True if merge succeeded, otherwise False.
        """
        if not self.is_configured():
            return False
        from github import GithubException
        try:
            pr = self.repo.get_pull(pr_number)
            status = pr.merge(commit_message=commit_message or f"Merged FQHE Agent PR #{pr_number}")
            logger.info(f"PR #{pr_number} merge status: {status.merged}")
            return status.merged
        except GithubException as e:
            logger.error(f"Error merging PR #{pr_number}: {e}")
            return False
