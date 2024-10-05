from gql import gql

from .base import BaseGitHubClient


class GitHubUsersClient(BaseGitHubClient):
    async def get(self, username: str):
        query = gql(
            """
            query getUser($username: String!) {
                user(login: $username) {
                    createdAt
                }
            }
            """
        )
        params = {"username": username}

        return await self._execute_query(query=query, params=params)
