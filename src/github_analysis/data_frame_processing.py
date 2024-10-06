import polars as pl

from .github.client.validators.contributions import GitHubPullRequestContribution
from .github.client.validators.pull_requests import GitHubPullRequest


def pull_request_reviews_as_data_frame(
    pull_request_reviews: list[GitHubPullRequestContribution],
):
    data_frame_data = {}

    return pl.DataFrame(data_frame_data)


def pull_requests_as_data_frame(pull_requests: list[GitHubPullRequest]):
    data_frame_data = {
        "created_at": [],
        "pull_request_number": [],
        "amount_of_comments": [],
        "repository_name": [],
    }
    for users_pull_request in pull_requests:
        data_frame_data["created_at"].append(users_pull_request.createdAt)
        data_frame_data["pull_request_number"].append(f"#{users_pull_request.number}")
        data_frame_data["amount_of_comments"].append(
            users_pull_request.comments.totalCount
        )
        data_frame_data["repository_name"].append(
            users_pull_request.baseRepository.nameWithOwner
        )

    return pl.DataFrame(data_frame_data).sort("created_at", descending=True)


def group_pull_requests_by_repositories(pull_requests: pl.DataFrame):
    return (
        pull_requests.group_by("repository_name")
        .agg(pl.len().alias("amount_of_pull_requests"))
        .sort("amount_of_pull_requests", descending=True)
    )
