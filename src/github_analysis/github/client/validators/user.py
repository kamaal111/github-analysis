from pydantic import BaseModel


class GitHubUser(BaseModel):
    login: str
