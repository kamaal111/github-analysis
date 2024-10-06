from datetime import datetime

from .client.client import GitHubClient
from .client.users import PullRequestStates
from .client.validators.contributions import GitHubPullRequestContribution
from .client.validators.pull_requests import GitHubPullRequest


class GitHubService:
    __client: GitHubClient

    def __init__(self) -> None:
        self.__client = GitHubClient()

    async def get_users_reviews(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        from_date: datetime | None = None,
    ) -> list[GitHubPullRequestContribution]:
        reviews = await self.__client.users.get_reviews(
            username=username,
            from_date=from_date,
            pagination_step_amount=pagination_step_amount,
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
    ) -> list[GitHubPullRequest]:
        return await self.__client.users.get_pull_requests(
            username=username,
            filter_states=filter_states,
            pagination_step_amount=pagination_step_amount,
            until=until,
        )
