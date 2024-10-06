from datetime import datetime

import polars as pl

from .client.client import GitHubClient
from .client.users import PullRequestStates


class GitHubService:
    __client: GitHubClient

    def __init__(self) -> None:
        self.__client = GitHubClient()

    async def get_users_pull_requests_as_data_frame(
        self,
        username: str,
        until: datetime | None = None,
        filter_states: list[PullRequestStates] = [],
    ) -> pl.DataFrame:
        users_pull_requests = await self.get_users_pull_requests(
            username=username, until=until, filter_states=filter_states
        )
        data_frame_data = {
            "created_at": [],
            "amount_of_comments": [],
            "repository_name": [],
        }
        for users_pull_request in users_pull_requests:
            data_frame_data["created_at"].append(users_pull_request.createdAt)
            data_frame_data["amount_of_comments"].append(
                users_pull_request.comments.totalCount
            )
            data_frame_data["repository_name"].append(
                users_pull_request.baseRepository.nameWithOwner
            )

        return pl.DataFrame(data_frame_data)

    async def get_users_pull_requests(
        self,
        username: str,
        until: datetime | None = None,
        filter_states: list[PullRequestStates] = [],
    ):
        return await self.__client.users.get_pull_requests(
            username=username, filter_states=filter_states, until=until
        )
