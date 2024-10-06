from pydantic import BaseModel


class GitHubRepository(BaseModel):
    nameWithOwner: str
