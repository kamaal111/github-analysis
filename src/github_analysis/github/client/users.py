from typing import Literal

from gql import gql

from .base import BaseGitHubClient

FilterStates = Literal["MERGED", "OPEN", "CLOSED"]


class GitHubUsersClient(BaseGitHubClient):
    async def get_pull_requests(
        self,
        username: str,
        filter_states: list[FilterStates] = [],
    ):
        query = gql(
            """
            query($username: String!, $filterStates: [PullRequestState!]) {
                user(login: $username) {
                    pullRequests(
                        last: 10,
                        orderBy: { field: CREATED_AT, direction: DESC },
                        states: $filterStates) {
                            nodes {
                                createdAt
                                author {
                                    login
                                }
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                                hasPreviousPage
                                startCursor
                            }
                            totalCount
                        }
                }
            }
            """
        )
        params = {"username": username, "filterStates": list(set(filter_states))}

        return await self._execute_query(query=query, params=params)
