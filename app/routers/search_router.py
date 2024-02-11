from fastapi import APIRouter, Body, HTTPException, Query
from app.models.search_result import SearchResult, SearchRequest
from app.services.google_search import search_google, find_leaders_by_name
from app.db.database import collection

router = APIRouter()

@router.get("/search")
async def search(query: str, page: int = Query(1, alias="page"), start_date: str = None, end_date: str = None, from_date: str = None, to_date: str = None, time_range: str = None,):
    search_results = await search_google(query, page,  from_date, to_date, time_range,)
    return search_results

@router.post("/http://localhost:8000/search?query=rahul+gandhi&time_range=custom&page=3&from_date=01/01/2024&to_date=01/31/2024/", response_model=list[SearchResult])
async def search_leaders(search_request: SearchRequest = Body(...)):
    results = await find_leaders_by_name(search_request.leader_name, search_request.page, search_request.page_size)
    if not results:
        raise HTTPException(status_code=404, detail="No results found")
    return results