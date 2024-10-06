from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Field, SQLModel


class PullRequestReviewsCache(SQLModel, table=True):
    __tablename__ = "pull_request_review_cache"
    __table_args__ = (
        UniqueConstraint(
            "username",
            "from_date",
            "fetch_date",
            name="pull_request_review_cache_entry",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    username: str
    from_date: str | None
    fetch_date: str
    items: str = Field(sa_type=JSON, nullable=False)
