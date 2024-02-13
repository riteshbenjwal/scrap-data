from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.models.search_result import SearchResult
from app.services.google_search import search_google
from app.services.youtube_search import search_youtube_service,fetch_video_details
from app.db.database import collection

router = APIRouter()


@router.get("/search")
async def search(query: str, page: int = Query(1, alias="page"), start_date: str = None, end_date: str = None, from_date: str = None, to_date: str = None, time_range: str = None,):
    search_results = await search_google(query, page,  from_date, to_date, time_range,)
    return search_results


@router.get("/videos/details")
async def search_youtube(query: str, page_token: str = Query(None, alias="pageToken"), max_results: int = Query(10, alias="maxResults"), order: str = Query("relevance", alias="order"), time_range: str = Query(None, alias="timeRange"), from_date: str = Query(None, alias="fromDate"), to_date: str = Query(None, alias="toDate")):
    search_results = await search_youtube_service(query, page_token, max_results, order, time_range, from_date, to_date)
    return search_results


@router.get("/youtube-video-details")
async def get_video_details(video_ids: List[str] = Query(...)):
    try:
        video_details = fetch_video_details(video_ids)
        return {"data": video_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))