from pydantic import BaseModel


class GitHubPageInfo(BaseModel):
    hasNextPage: bool
    hasPreviousPage: bool
    endCursor: str
    startCursor: str
