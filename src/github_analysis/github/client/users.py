from datetime import datetime
from typing import Any, Literal

from gql import gql
from gql.client import AsyncClientSession, ReconnectingAsyncClientSession

from .base import BaseGitHubClient
from .validators.contributions import (
    GitHubPullRequestContribution,
    GitHubPullRequestContributionsGraph,
)
from .validators.pull_requests import GitHubPullRequest, GitHubPullRequestGraph

PullRequestStates = Literal["MERGED", "OPEN", "CLOSED"]


DEFAULT_PER_PAGE_AMOUNT = 100


class GitHubUsersClient(BaseGitHubClient):
    async def get_reviews(
        self,
        username: str,
        from_date: datetime | None = None,
        pagination_step_amount: int | None = None,
        session: AsyncClientSession | ReconnectingAsyncClientSession | None = None,
    ):
        query = gql(
            """
            query($username: String!, $fromDate: DateTime, $perPageAmount: Int!, $beforeCursor: String) {
                user(login: $username) {
                    contributionsCollection(from: $fromDate) {
                        pullRequestReviewContributions(
                            last: $perPageAmount,
                            orderBy: { direction: ASC },
                            before: $beforeCursor
                        ) {
                            nodes {
                                pullRequestReview {
                                    author {
                                        login
                                    }
                                }
                                repository {
                                    nameWithOwner
                                }
                                pullRequest {
                                    createdAt
                                    comments {
                                        totalCount
                                    }
                                    baseRepository {
                                        nameWithOwner
                                    }
                                    number
                                    author {
                                        login
                                    }
                                }
                            }
                            pageInfo {
                                hasPreviousPage
                                startCursor
                            }
                        }
                    }
                }
            }
            """
        )
        params = {
            "username": username,
            "from": None,
            "perPageAmount": pagination_step_amount
            if pagination_step_amount is not None
            else DEFAULT_PER_PAGE_AMOUNT,
            "beforeCursor": None,
        }
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        def get_pull_requests_review_contributions(result: dict[str, Any]):
            validated_result = GitHubPullRequestContributionsGraph(
                **result.get("user", {}).get("contributionsCollection")
            )

            return validated_result.pullRequestReviewContributions

        def get_nodes(result: dict[str, Any]):
            return get_pull_requests_review_contributions(result).nodes

        def get_page_info(result: dict[str, Any]):
            return get_pull_requests_review_contributions(result).pageInfo

        def get_create_at_from_node(node: GitHubPullRequestContribution):
            return node.pullRequest.createdAt

        return await self._paginate_nodes_request_in_reverse(
            query=query,
            params=params,
            get_nodes=get_nodes,
            get_page_info=get_page_info,
            session=session,
            get_create_at_from_node=get_create_at_from_node,
            fetch_all=True,
        )

    async def get_pull_requests(
        self,
        username: str,
        pagination_step_amount: int | None = None,
        until: datetime | None = None,
        filter_states: list[PullRequestStates] = [],
        session: AsyncClientSession | ReconnectingAsyncClientSession | None = None,
    ) -> list[GitHubPullRequest]:
        query = gql(
            """
            query($username: String!, $filterStates: [PullRequestState!], $beforeCursor: String, $perPageAmount: Int!) {
                user(login: $username) {
                    pullRequests(
                        last: $perPageAmount,
                        orderBy: { field: CREATED_AT, direction: ASC },
                        states: $filterStates,
                        before: $beforeCursor
                    ) {
                        nodes {
                            createdAt
                            author {
                                login
                            }
                            comments {
                                totalCount
                            }
                            baseRepository {
                                nameWithOwner
                            }
                            number
                            participants(first: 20) {
                                nodes {
                                    login
                                }
                            }
                        }
                        pageInfo {
                            hasPreviousPage
                            startCursor
                        }
                    }
                }
            }
            """
        )
        params = {
            "username": username,
            "filterStates": list(set(filter_states)),
            "beforeCursor": None,
            "perPageAmount": pagination_step_amount
            if pagination_step_amount is not None
            else DEFAULT_PER_PAGE_AMOUNT,
        }

        def get_pull_requests(result: dict[str, Any]):
            validated_result = GitHubPullRequestGraph(**result.get("user"))

            return validated_result.pullRequests

        def get_nodes(result: dict[str, Any]):
            return get_pull_requests(result).nodes

        def get_page_info(result: dict[str, Any]):
            return get_pull_requests(result).pageInfo

        def get_create_at_from_node(node: GitHubPullRequest):
            return node.createdAt

        return await self._paginate_nodes_request_in_reverse(
            query=query,
            params=params,
            get_nodes=get_nodes,
            get_page_info=get_page_info,
            session=session,
            get_create_at_from_node=get_create_at_from_node,
            until=until,
        )
