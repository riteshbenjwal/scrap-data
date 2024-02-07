from pydantic import BaseModel

class SearchResult(BaseModel):
    leader_name: str
    link: str
    author: str = None
    headline: str
    description: str
