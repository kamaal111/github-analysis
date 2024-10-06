from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Field, SQLModel


class PullRequestsCache(SQLModel, table=True):
    __tablename__ = "pull_requests_cache"
    __table_args__ = (
        UniqueConstraint(
            "username",
            "until",
            "fetch_date",
            "filter_states",
            name="pull_requests_cache_entry",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    username: str
    until: str | None
    fetch_date: str
    filter_states: str = Field(sa_type=JSON, nullable=False)
    items: str = Field(sa_type=JSON, nullable=False)
