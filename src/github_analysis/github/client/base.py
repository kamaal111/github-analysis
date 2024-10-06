import os
from pathlib import Path
from typing import Any, Callable, TypeVar

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode

from ..settings import settings
from .dataclasses.filter_data import FilterData
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
        filter_data: FilterData[ItemNode] | None = None,
    ) -> list[ItemNode]:
        new_params = {**(params or {}), "beforeCursor": None}
        nodes: list[ItemNode] = []
        while True:
            result = await self._execute_query(query=query, params=new_params)
            fetched_nodes = get_nodes(result)
            nodes = nodes + fetched_nodes

            if filter_data is None:
                return nodes

            page_info = get_page_info(result)
            if not page_info.hasPreviousPage:
                break

            if len(fetched_nodes) == 0:
                break

            if (
                filter_data.get_create_at_from_node(fetched_nodes[0])
                < filter_data.until
            ):
                break

            new_params["beforeCursor"] = page_info.startCursor

        if filter_data is None:
            return nodes

        def filter_node(node: ItemNode):
            return filter_data.get_create_at_from_node(node) < filter_data.until

        return sorted(
            filter(filter_node, nodes), key=filter_data.get_create_at_from_node
        )

    @staticmethod
    def __setup_gql_client():
        gql_transport = AIOHTTPTransport(
            url=os.path.join(settings.github_base_url_string, "graphql"),
            headers={"Authorization": f"bearer {settings.github_token}"},
        )
        graphql_api_schema = Path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "schemas/github_api.graphql",
            )
        )

        return Client(transport=gql_transport, schema=graphql_api_schema.read_text())
