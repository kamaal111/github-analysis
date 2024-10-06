from datetime import datetime

from gql.client import AsyncClientSession, ReconnectingAsyncClientSession

from .client.client import GitHubClient
from .client.users import PullRequestStates
from .client.validators.contributions import GitHubPullRequestContribution
from .client.validators.pull_requests import GitHubPullRequest


class GitHubService:
    __client: GitHubClient

    def __init__(self) -> None:
        self.__client = GitHubClient()

    async def get_users_reviews_and_pull_requests(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        from_date: datetime | None = None,
        pull_request_states: list[PullRequestStates] = [],
    ) -> tuple[list[GitHubPullRequestContribution], list[GitHubPullRequest]]:
        return await self.__client.gather(
            [
                lambda session: self.get_users_reviews(
                    username=username,
                    pagination_step_amount=pagination_step_amount,
                    from_date=from_date,
                    session=session,
                ),
                lambda session: self.get_users_pull_requests(
                    username=username,
                    pagination_step_amount=pagination_step_amount,
                    until=from_date,
                    filter_states=pull_request_states,
                    session=session,
                ),
            ]
        )

    async def get_users_reviews(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        from_date: datetime | None = None,
        session: AsyncClientSession | ReconnectingAsyncClientSession | None = None,
    ) -> list[GitHubPullRequestContribution]:
        reviews = await self.__client.users.get_reviews(
            username=username,
            from_date=from_date,
            pagination_step_amount=pagination_step_amount,
            session=session,
        )

        def filter_review(review: GitHubPullRequestContribution):
            pull_request_author = review.pullRequest.author
            if pull_request_author is None:
                return True

            pull_request_author_login = pull_request_author.login
            reviewer = review.pullRequestReview.author.login

            return reviewer != pull_request_author_login

        return list(filter(filter_review, reviews))

    async def get_users_pull_requests(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        until: datetime | None = None,
        filter_states: list[PullRequestStates] = [],
        session: AsyncClientSession | ReconnectingAsyncClientSession | None = None,
    ) -> list[GitHubPullRequest]:
        return await self.__client.users.get_pull_requests(
            username=username,
            filter_states=filter_states,
            pagination_step_amount=pagination_step_amount,
            until=until,
            session=session,
        )
