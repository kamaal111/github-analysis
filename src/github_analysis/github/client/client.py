import asyncio
import os
from asyncio import Task
from pathlib import Path
from typing import Callable, Coroutine

from gql import Client
from gql.client import AsyncClientSession, ReconnectingAsyncClientSession
from gql.transport.aiohttp import AIOHTTPTransport

from ..settings import settings
from .users import GitHubUsersClient


class GitHubClient:
    users: GitHubUsersClient
    __gql_client: Client

    def __init__(self) -> None:
        self.__gql_client = GitHubClient.__setup_gql_client()
        self.users = GitHubUsersClient(gcl_client=self.__gql_client)

    async def gather(
        self,
        tasks: list[
            Callable[[AsyncClientSession | ReconnectingAsyncClientSession], Coroutine]
        ],
    ):
        async with self.__gql_client as session:
            tasks_to_gather: list[Task] = []
            for coroutine in tasks:
                tasks_to_gather.append(asyncio.create_task(coroutine(session)))

            return await asyncio.gather(*tasks_to_gather)

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
