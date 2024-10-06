from pydantic import BaseModel


class GitHubAuthor(BaseModel):
    login: str
