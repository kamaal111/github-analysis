from pydantic import BaseModel


class GitHubPageInfo(BaseModel):
    hasPreviousPage: bool
    startCursor: str
