from .users import GitHubUsersClient


class GitHubClient:
    users: GitHubUsersClient

    def __init__(self) -> None:
        self.users = GitHubUsersClient()
