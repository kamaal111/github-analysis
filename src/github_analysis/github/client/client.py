from .users import GitHubUsersClient


class GitHubClient:
    user: GitHubUsersClient

    def __init__(self) -> None:
        self.users = GitHubUsersClient()
