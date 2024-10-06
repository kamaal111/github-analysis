from datetime import datetime

from .client.client import GitHubClient
from .client.users import PullRequestStates


class GitHubService:
    __client: GitHubClient

    def __init__(self) -> None:
        self.__client = GitHubClient()

    async def get_users_reviews(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        from_date: datetime | None = None,
    ):
        return await self.__client.users.get_reviews(
            username=username,
            from_date=from_date,
            pagination_step_amount=pagination_step_amount,
        )

    async def get_users_pull_requests(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        until: datetime | None = None,
        filter_states: list[PullRequestStates] = [],
    ):
        return await self.__client.users.get_pull_requests(
            username=username,
            filter_states=filter_states,
            pagination_step_amount=pagination_step_amount,
            until=until,
        )
