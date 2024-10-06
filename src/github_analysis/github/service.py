import json
from datetime import datetime, timezone

from gql.client import AsyncClientSession, ReconnectingAsyncClientSession
from sqlmodel import Session, select

from github_analysis.database.database import database

from .client.client import GitHubClient
from .client.users import PullRequestStates
from .client.validators.contributions import GitHubPullRequestContribution
from .client.validators.pull_requests import GitHubPullRequest
from .models.contributions import PullRequestReviewsCache
from .models.pull_requests import PullRequestsCache


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
        cache = self.__get_users_reviews_cache(username=username, from_date=from_date)
        if cache is not None:
            return cache

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

        filter_result = list(filter(filter_review, reviews))
        self.__set_users_reviews_cache(
            username=username, from_date=from_date, result=filter_result
        )

        return filter_result

    async def get_users_pull_requests(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        until: datetime | None = None,
        filter_states: list[PullRequestStates] = [],
        session: AsyncClientSession | ReconnectingAsyncClientSession | None = None,
    ) -> list[GitHubPullRequest]:
        cache = self.__get_users_pull_requests_cache(
            username=username, until=until, filter_states=filter_states
        )
        if cache is not None:
            return cache

        result = await self.__client.users.get_pull_requests(
            username=username,
            filter_states=filter_states,
            pagination_step_amount=pagination_step_amount,
            until=until,
            session=session,
        )
        self.__set_users_pull_requests_cache(
            username=username, until=until, filter_states=filter_states, result=result
        )

        return result

    def __get_users_reviews_cache(self, username: str, from_date: datetime | None):
        fetch_date_key = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        from_date_key = from_date.strftime("%Y-%m-%d") if from_date else None

        with Session(database.engine) as session:
            cache_query = (
                select(PullRequestReviewsCache)
                .where(PullRequestReviewsCache.fetch_date == fetch_date_key)
                .where(PullRequestReviewsCache.from_date == from_date_key)
                .where(PullRequestReviewsCache.username == username)
                .limit(1)
            )
            if cache := session.exec(cache_query).first():
                parsed: list[GitHubPullRequestContribution] = []
                for item in json.loads(cache.items):
                    parsed.append(GitHubPullRequestContribution(**item))

                return parsed

    def __get_users_pull_requests_cache(
        self,
        username: str,
        until: datetime | None,
        filter_states: list[PullRequestStates],
    ):
        fetch_date_key = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        until_key = until.strftime("%Y-%m-%d") if until else None

        with Session(database.engine) as session:
            cache_query = (
                select(PullRequestsCache)
                .where(PullRequestsCache.fetch_date == fetch_date_key)
                .where(PullRequestsCache.until == until_key)
                .where(PullRequestsCache.username == username)
                .limit(1)
            )
            if caches := session.exec(cache_query).all():
                for cache in caches:
                    if sorted(set(json.loads(cache.filter_states))) == sorted(
                        set(filter_states)
                    ):
                        parsed: list[GitHubPullRequest] = []
                        for item in json.loads(cache.items):
                            parsed.append(GitHubPullRequest(**item))

                        return parsed

    def __set_users_reviews_cache(
        self,
        username: str,
        from_date: datetime | None,
        result: list[GitHubPullRequestContribution],
    ):
        dict_list = []
        for item in result:
            dict_list.append(item.model_dump(mode="json"))

        fetch_date_key = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        from_date_key = from_date.strftime("%Y-%m-%d") if from_date else None
        cache = PullRequestReviewsCache(
            username=username,
            from_date=from_date_key,
            fetch_date=fetch_date_key,
            items=json.dumps(dict_list),
        )

        with Session(database.engine) as session:
            session.add(cache)
            session.commit()

    def __set_users_pull_requests_cache(
        self,
        username: str,
        until: datetime | None,
        filter_states: list[PullRequestStates],
        result: list[GitHubPullRequest],
    ):
        dict_list = []
        for item in result:
            dict_list.append(item.model_dump(mode="json"))

        fetch_date_key = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        until_key = until.strftime("%Y-%m-%d") if until else None
        filter_states_key = json.dumps(sorted(set(filter_states)))
        cache = PullRequestsCache(
            username=username,
            until=until_key,
            fetch_date=fetch_date_key,
            filter_states=filter_states_key,
            items=json.dumps(dict_list),
        )

        with Session(database.engine) as session:
            session.add(cache)
            session.commit()
