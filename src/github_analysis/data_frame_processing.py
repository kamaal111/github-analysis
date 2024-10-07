import polars as pl

from .github.client.validators.contributions import GitHubPullRequestContribution
from .github.client.validators.pull_requests import GitHubPullRequest


def pull_request_reviews_as_data_frame(
    pull_request_reviews: list[GitHubPullRequestContribution],
):
    data_frame_data = {
        "created_at": [],
        "author": [],
        "amount_of_comments": [],
        "repository_name": [],
        "pull_request_number": [],
    }
    for pull_request_review in pull_request_reviews:
        pull_request_author = pull_request_review.pullRequest.author
        data_frame_data["author"].append(
            pull_request_author.login if pull_request_author is not None else None
        )
        data_frame_data["repository_name"].append(
            pull_request_review.repository.nameWithOwner
        )
        data_frame_data["amount_of_comments"].append(
            pull_request_review.pullRequest.comments.totalCount
        )
        data_frame_data["pull_request_number"].append(
            f"#{pull_request_review.pullRequest.number}"
        )
        data_frame_data["created_at"].append(pull_request_review.pullRequest.createdAt)

    return pl.DataFrame(data_frame_data).sort("created_at", descending=True)


def process_total_stats(
    grouped_pull_request_reviews: pl.DataFrame,
    grouped_merged_pull_requests: pl.DataFrame,
):
    return pl.DataFrame(
        {
            "stat": ["reviews", "pull_requests"],
            "totals": [
                grouped_pull_request_reviews.get_column("amount_of_reviews").sum(),
                grouped_merged_pull_requests.get_column(
                    "amount_of_pull_requests"
                ).sum(),
            ],
        }
    )


def group_pull_request_reviews_by_repositories(pull_request_reviews: pl.DataFrame):
    return (
        pull_request_reviews.filter(pl.col("amount_of_comments") == 0)
        .group_by("repository_name")
        .agg(pl.len().alias("amount_of_reviews"))
        .sort("amount_of_reviews", descending=True)
    )


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
