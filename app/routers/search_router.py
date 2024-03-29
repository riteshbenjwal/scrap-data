from fastapi import APIRouter, Query, HTTPException,Depends
from typing import List
from app.services.google_search import search_google

from pydantic import BaseModel
from typing import Optional
from app.services.track_leader import add_track_leader

router = APIRouter()

@router.get("/search")
async def search(leader_name: str = Query(None, alias="leader_name"), 
 keywords: str = Query(None, alias="keywords"), hash_tag: str = Query(None, alias="hash_tag"), twitter_handle: str = Query(None, alias="twitter_handle"), facebook_id: str = Query(None, alias="facebook_id"), instagram_id: str = Query(None, alias="instagram_id"),page: int = Query(1, alias="page"), start_date: str = None, end_date: str = None, from_date: str = None, to_date: str = None, time_range: str = None):
    search_results = await search_google(leader_name, page,  from_date, to_date, time_range,)
    return search_results



from pydantic import BaseModel, Field
from typing import Optional

class Leader(BaseModel):
    user_id: Optional[str] = None
    leader_name: str = Field(..., example="John Doe")
    keywords: Optional[str] = None
    hash_tag: Optional[str] = None
    twitter_handle: Optional[str] = None
    facebook_id: Optional[str] = None
    instagram_id: Optional[str] = None
    frequency_update: Optional[str] = None




# {
#     // "user_id": "12345",
#     "leader_name": "sushma swaraj",
#     "keywords": "bjp, minister",
#     "hash_tag": "#externalaffairminister",
#     "twitter_handle": "@janedoe",
#     "facebook_id": "janedoeFB",
#     "instagram_id": "janedoeInsta"
#     // "frequency_update": "daily"
# }


@router.post("/track-leaders")
async def track_leaders(leader: Leader):
    try:
        return await add_track_leader(leader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



