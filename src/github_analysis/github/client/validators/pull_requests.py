from datetime import datetime

from pydantic import BaseModel

from .page_info import GitHubPageInfo


class GitHubComments(BaseModel):
    totalCount: int


class GitHubAuthor(BaseModel):
    login: str


class GitHubRepository(BaseModel):
    name: str
    nameWithOwner: str


class GitHubPullRequest(BaseModel):
    createdAt: datetime
    author: GitHubAuthor
    comments: GitHubComments
    baseRepository: GitHubRepository


class GitHubPullRequests(BaseModel):
    nodes: list[GitHubPullRequest]
    totalCount: int
    pageInfo: GitHubPageInfo


class GitHubUsersPullRequest(BaseModel):
    pullRequests: GitHubPullRequests


class GitHubUsersPullRequestResult(BaseModel):
    user: GitHubUsersPullRequest
