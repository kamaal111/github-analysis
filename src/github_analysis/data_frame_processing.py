from functools import reduce

import narwhals as nw
import polars as pl

from .github.client.validators.contributions import GitHubPullRequestContribution
from .github.client.validators.pull_requests import GitHubPullRequest


def pull_request_reviews_as_data_frame(
    pull_request_reviews: list[GitHubPullRequestContribution],
) -> nw.LazyFrame[pl.LazyFrame]:
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

    data_frame = nw.from_native(pl.LazyFrame(data_frame_data))
    assert isinstance(data_frame, nw.LazyFrame)

    return data_frame.sort("created_at", descending=True)


def reviews_given_to_user(
    pull_request_reviews: nw.LazyFrame[pl.LazyFrame],
) -> nw.LazyFrame[pl.LazyFrame]:
    return (
        pull_request_reviews.group_by("author")
        .agg(nw.len().alias("pull_request_reviews_given"))
        .sort("pull_request_reviews_given", descending=True)
        .rename({"author": "pull_request_author"})
    )


def reviews_given_by_users(
    pull_requests: nw.LazyFrame[pl.LazyFrame],
) -> nw.LazyFrame[pl.LazyFrame]:
    data_frame = nw.from_native(
        pl.LazyFrame(
            {
                "reviewer": reduce(
                    lambda acc, reviewers: acc + reviewers,
                    pull_requests.collect().get_column("reviewers").to_list(),
                    [],
                )
            }
        )
    )
    assert isinstance(data_frame, nw.LazyFrame)

    return (
        data_frame.group_by("reviewer")
        .agg(nw.len().alias("reviews_given"))
        .sort("reviews_given", descending=True)
    )


def pull_requests_aggregated_by_month(
    pull_requests: nw.LazyFrame[pl.LazyFrame],
) -> nw.LazyFrame[pl.LazyFrame]:
    created_at_date = nw.col("created_at").dt
    created_at_month = created_at_date.month()
    created_at_year = created_at_date.year()

    return (
        pull_requests.with_columns(
            nw.concat_str(
                [
                    created_at_month.cast(nw.String),
                    nw.lit("-"),
                    (created_at_year % 100).cast(nw.String),
                ]
            ).alias("created_at_month"),
            ((created_at_year * 12) + (created_at_month - 1)).alias("months_weight"),
        )
        .group_by("created_at_month")
        .agg(
            nw.len().alias("amount_pull_requests"),
            nw.col("months_weight").head(1).max(),
        )
        .select("created_at_month", "amount_pull_requests")
        .sort("months_weight", descending=True)
    )


def process_total_stats(
    grouped_pull_request_reviews: nw.LazyFrame[pl.LazyFrame],
    grouped_merged_pull_requests: nw.LazyFrame[pl.LazyFrame],
) -> nw.LazyFrame[pl.LazyFrame]:
    collected_grouped_pull_request_reviews = grouped_pull_request_reviews.collect()
    data_frame = nw.from_native(
        pl.LazyFrame(
            {
                "stat": [
                    "pull_request_reviews",
                    "instant_approve_reviews",
                    "pull_requests",
                ],
                "totals": [
                    collected_grouped_pull_request_reviews.get_column(
                        "amount_of_reviews"
                    ).sum(),
                    collected_grouped_pull_request_reviews.get_column(
                        "instant_approve_reviews"
                    ).sum(),
                    grouped_merged_pull_requests.collect()
                    .get_column("amount_of_pull_requests")
                    .sum(),
                ],
            }
        )
    )
    assert isinstance(data_frame, nw.LazyFrame)

    return data_frame


def group_pull_request_reviews_by_repositories(
    pull_request_reviews: nw.LazyFrame[pl.LazyFrame],
) -> nw.LazyFrame[pl.LazyFrame]:
    return (
        pull_request_reviews.with_columns(
            nw.col("amount_of_comments")
            .clip(upper_bound=1)
            .alias("amount_of_comments_binary")
        )
        .group_by("repository_name")
        .agg(
            nw.len().alias("amount_of_reviews"),
            nw.sum("amount_of_comments_binary").alias(
                "amount_of_reviews_with_comments"
            ),
            nw.col("amount_of_comments").sum().alias("total_amount_of_comments_given"),
            nw.col("amount_of_comments")
            .mean()
            .alias("average_amount_of_comments_per_pull_request"),
        )
        .with_columns(
            (
                nw.col("amount_of_reviews") - nw.col("amount_of_reviews_with_comments")
            ).alias("instant_approve_reviews"),
        )
        .select(
            "repository_name",
            "amount_of_reviews",
            "instant_approve_reviews",
            "total_amount_of_comments_given",
            "average_amount_of_comments_per_pull_request",
        )
        .sort("amount_of_reviews", descending=True)
    )


def pull_requests_as_data_frame(
    pull_requests: list[GitHubPullRequest],
) -> nw.LazyFrame[pl.LazyFrame]:
    data_frame_data = {
        "created_at": [],
        "pull_request_number": [],
        "amount_of_comments": [],
        "repository_name": [],
        "reviewers": [],
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
        reviewers: set[str] = set()
        if users_pull_request.participants:
            for participant in users_pull_request.participants.nodes:
                if (
                    author := users_pull_request.author
                ) and author.login != participant.login:
                    reviewers.add(participant.login)
        data_frame_data["reviewers"].append(list(reviewers))

    data_frame = nw.from_native(pl.LazyFrame(data_frame_data))
    assert isinstance(data_frame, nw.LazyFrame)

    return data_frame.sort("created_at", descending=True)


def group_pull_requests_by_repositories(
    pull_requests: nw.LazyFrame[pl.LazyFrame],
) -> nw.LazyFrame[pl.LazyFrame]:
    return (
        pull_requests.group_by("repository_name")
        .agg(nw.len().alias("amount_of_pull_requests"))
        .sort("amount_of_pull_requests", descending=True)
    )
