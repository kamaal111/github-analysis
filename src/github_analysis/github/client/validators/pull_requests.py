from datetime import datetime

from pydantic import BaseModel

from .author import GitHubAuthor
from .page_info import GitHubPageInfo
from .repository import GitHubRepository


class GitHubComments(BaseModel):
    totalCount: int


class GitHubPullRequest(BaseModel):
    createdAt: datetime
    author: GitHubAuthor
    comments: GitHubComments
    baseRepository: GitHubRepository
    number: int


class GitHubPullRequests(BaseModel):
    nodes: list[GitHubPullRequest]
    pageInfo: GitHubPageInfo


class GitHubPullRequestGraph(BaseModel):
    pullRequests: GitHubPullRequests
