import requests
from fastapi import HTTPException, Query
from app.config import API_KEY, CSE_ID, MONGODB_URI
from app.repository.db_repo import insert_search_results
from app.utility.date_utils import get_date_range
# Corrected import statement for AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorClient

db = AsyncIOMotorClient('mongodb_uri').your_database
async def search_google(query: str, page: int = Query(1, alias="page"), from_date: str = None, to_date: str = None, time_range: str = None):
    search_url = "https://www.googleapis.com/customsearch/v1"
    # Calculate the start index based on the page number
    start_index = (page - 1) * 10 + 1
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "start": start_index,
    }
    # Handle date range search
    if time_range == "custom" and from_date and to_date:
        # Custom date range specified by from_date and to_date
        start_date_str, end_date_str = get_date_range(time_range, from_date, to_date)
    elif time_range:
        # Predefined time ranges like "Past month", "Past year", etc.
        start_date_str, end_date_str = get_date_range(time_range)
    else:
        print("else")
        start_date_str = end_date_str = None

    if start_date_str and end_date_str:
        params["sort"] = f"date:r:{start_date_str}:{end_date_str}"
    # if start_date and end_date:
    #     params["dateRestrict"] = f"d[{start_date},{end_date}]"

    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        # Extract and store relevant information from items in the response
        items = response.json().get('items', [])
        search_results = []
        for item in items:
            leader_name = query
            link = item.get('link')
            author = None  # No author provided in the response
            headline = item.get('title')
            description = item.get('snippet')
            search_result = {
                "leader_name": leader_name,
                "link": link,
                "author": author,
                "headline": headline,
                "description": description
            }
            search_results.append(search_result)

        # Insert search results into MongoDB
        if search_results:
              # Use the repository layer to interact with the database
            insert_search_results(search_results)

        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

async def find_leaders_by_name(leader_name: str, page: int, page_size: int):
    skip = (page - 1) * page_size
    cursor = db.your_collection_name.find({"leader_name": leader_name}).skip(skip).limit(page_size)
    results = await cursor.to_list(length=page_size)
    if not results:
        raise HTTPException(status_code=404, detail="Leader not found")
    return results