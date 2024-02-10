from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    leader_name: str
    link: str
    author: str = None
    headline: str
    description: str

class SearchRequest(BaseModel):
    leader_name: str
    page: int = Field(default=1, ge=1, description="Page number starting from 1")
    page_size: int = Field(default=10, ge=1, le=100, description="Number of items per page, max 100")