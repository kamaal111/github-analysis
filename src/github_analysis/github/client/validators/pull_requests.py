from datetime import datetime

from pydantic import BaseModel

from .page_info import GitHubPageInfo
from .repository import GitHubRepository
from .user import GitHubUser


class GitHubComments(BaseModel):
    totalCount: int


class GitHubPullRequestParticipantsGraph(BaseModel):
    nodes: list[GitHubUser]


class GitHubPullRequest(BaseModel):
    createdAt: datetime
    author: GitHubUser | None = None
    comments: GitHubComments
    baseRepository: GitHubRepository
    number: int
    participants: GitHubPullRequestParticipantsGraph | None = None


class GitHubPullRequests(BaseModel):
    nodes: list[GitHubPullRequest]
    pageInfo: GitHubPageInfo


class GitHubPullRequestGraph(BaseModel):
    pullRequests: GitHubPullRequests
