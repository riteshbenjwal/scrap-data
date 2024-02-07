import requests
from fastapi import HTTPException, Query
from app.config import API_KEY, CSE_ID, MONGODB_URI
from app.repository.db_repo import insert_search_results  

async def search_google(query: str, page: int = Query(1, alias="page"), start_date: str = None, end_date: str = None):
    
    search_url = "https://www.googleapis.com/customsearch/v1"
 # Calculate the start index based on the page number
    start_index = (page - 1) * 10 + 1

    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "start": start_index,
    }
    
    # If date range is provided, add it to the search parameters
    if start_date and end_date:
        params["dateRestrict"] = f"d[{start_date},{end_date}]"

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
