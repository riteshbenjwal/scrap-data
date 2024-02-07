from fastapi import APIRouter, Query
from app.models.search_result import SearchResult
from app.services.google_search import search_google
from app.db.database import collection

router = APIRouter()

@router.get("/search")
async def search(query: str, page: int = Query(1, alias="page"), start_date: str = None, end_date: str = None):
    search_results = await search_google(query, page, start_date, end_date)
    return search_results
