from datetime import datetime
from typing import Any, Literal

from gql import gql

from .base import BaseGitHubClient
from .dataclasses.filter_data import FilterData
from .validators.pull_requests import GitHubPullRequest, GitHubUsersPullRequestResult

PullRequestStates = Literal["MERGED", "OPEN", "CLOSED"]


PER_PAGE_AMOUNT = 10


class GitHubUsersClient(BaseGitHubClient):
    async def get_pull_requests(
        self,
        username: str,
        until: datetime | None = None,
        filter_states: list[PullRequestStates] = [],
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
                        }
                        pageInfo {
                            hasNextPage
                            hasPreviousPage
                            endCursor
                            startCursor
                        }
                        totalCount
                    }
                }
            }
            """
        )
        params = {
            "username": username,
            "filterStates": list(set(filter_states)),
            "beforeCursor": None,
            "perPageAmount": PER_PAGE_AMOUNT,
        }

        def get_pull_requests(result: dict[str, Any]):
            validated_result = GitHubUsersPullRequestResult(**result)

            return validated_result.user.pullRequests

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
            filter_data=FilterData(
                until=until,
                get_create_at_from_node=get_create_at_from_node,
            ),
        )
