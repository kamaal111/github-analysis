from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///database.db"


class __Database:
    engine: "Engine"

    def __init__(self) -> None:
        self.engine = create_engine(DATABASE_URL, echo=False)

    def _create_db_and_tables(self):
        # Import models that need to be created here
        from github_analysis.github.models.contributions import (
            PullRequestReviewsCache,  # noqa: F401
        )
        from github_analysis.github.models.pull_requests import (
            PullRequestsCache,  # noqa: F401
        )

        SQLModel.metadata.create_all(self.engine)


database = __Database()

database._create_db_and_tables()
