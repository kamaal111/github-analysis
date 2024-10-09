from pydantic import BaseModel

from .page_info import GitHubPageInfo
from .pull_requests import GitHubPullRequest
from .repository import GitHubRepository
from .user import GitHubUser


class GitHubPullRequestReview(BaseModel):
    author: GitHubUser


class GitHubPullRequestContribution(BaseModel):
    pullRequestReview: GitHubPullRequestReview
    repository: GitHubRepository
    pullRequest: GitHubPullRequest


class GitHubPullRequestContributions(BaseModel):
    nodes: list[GitHubPullRequestContribution]
    pageInfo: GitHubPageInfo


class GitHubPullRequestContributionsGraph(BaseModel):
    pullRequestReviewContributions: GitHubPullRequestContributions
