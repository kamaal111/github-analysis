from pydantic import BaseModel

from .author import GitHubAuthor
from .page_info import GitHubPageInfo
from .pull_requests import GitHubPullRequest
from .repository import GitHubRepository


class GitHubPullRequestReview(BaseModel):
    author: GitHubAuthor


class GitHubPullRequestContribution(BaseModel):
    pullRequestReview: GitHubPullRequestReview
    repository: GitHubRepository
    pullRequest: GitHubPullRequest


class GitHubPullRequestContributions(BaseModel):
    nodes: list[GitHubPullRequestContribution]
    pageInfo: GitHubPageInfo


class GitHubPullRequestContributionsGraph(BaseModel):
    pullRequestReviewContributions: GitHubPullRequestContributions
