import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypeVar

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode

from ..settings import settings
from .validators.page_info import GitHubPageInfo

ItemNode = TypeVar("ItemNode")


class BaseGitHubClient:
    __gql_client: Client

    def __init__(self) -> None:
        self.__gql_client = BaseGitHubClient.__setup_gql_client()

    async def _execute_query(
        self, query: DocumentNode, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        async with self.__gql_client as session:
            return await session.execute(query, variable_values=params)

    async def _paginate_nodes_request_in_reverse(
        self,
        query: DocumentNode,
        params: dict[str, Any] | None,
        get_nodes: Callable[[dict[str, Any]], list[ItemNode]],
        get_page_info: Callable[[dict[str, Any]], GitHubPageInfo],
        get_create_at_from_node: Callable[[ItemNode], datetime],
        fetch_all: bool = False,
        until: datetime = None,
    ) -> list[ItemNode]:
        new_params = {**(params or {}), "beforeCursor": None}
        nodes: list[ItemNode] = []

        def node_is_less_then_until(node: ItemNode):
            if fetch_all:
                return True

            if until is None:
                return False

            return get_create_at_from_node(node) >= until

        while True:
            result = await self._execute_query(query=query, params=new_params)
            fetched_nodes = get_nodes(result)
            nodes = nodes + fetched_nodes

            page_info = get_page_info(result)
            if not page_info.hasPreviousPage:
                break

            if len(fetched_nodes) == 0:
                break

            if not node_is_less_then_until(fetched_nodes[0]):
                break

            new_params["beforeCursor"] = page_info.startCursor

        return sorted(
            filter(node_is_less_then_until, nodes),
            key=get_create_at_from_node,
        )

    @staticmethod
    def __setup_gql_client():
        gql_transport = AIOHTTPTransport(
            url=os.path.join(settings.github_api_base_url_string, "graphql"),
            headers={"Authorization": f"bearer {settings.github_token}"},
        )
        graphql_api_schema = Path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "schemas/github_api.graphql",
            )
        )

        return Client(transport=gql_transport, schema=graphql_api_schema.read_text())
