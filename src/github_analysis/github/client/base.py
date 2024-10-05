import os
from pathlib import Path
from typing import Any

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode

from ..settings import settings


class BaseGitHubClient:
    __gql_client: Client

    def __init__(self) -> None:
        self.__gql_client = BaseGitHubClient.__setup_gql_client()

    async def _execute_query(
        self, query: DocumentNode, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        async with self.__gql_client as session:
            return await session.execute(query, variable_values=params)

    @staticmethod
    def __setup_gql_client():
        gql_transport = AIOHTTPTransport(
            url=f"{settings.github_base_url}/graphql",
            headers={"Authorization": f"bearer {settings.github_token}"},
        )
        graphql_api_schema = Path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "schemas/github_api.graphql",
            )
        )

        return Client(transport=gql_transport, schema=graphql_api_schema.read_text())
