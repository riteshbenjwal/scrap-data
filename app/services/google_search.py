import requests
from fastapi import HTTPException, Query
from app.config import API_KEY, CSE_ID
from app.repository.db_repo import insert_search_results
from app.utility.date_utils import get_date_range
from urllib.parse import urlparse

social_media_domains = {
    'Instagram': ['instagram.com', 'instagr.am', 'help.instagram.com', 'm.instagram.com', 'ig.me', 'applink.instagram.com', 'call.instagram.com'],
    'Facebook': ['facebook.com', 'fb.com', 'messenger.com'],
    'Twitter': ['twitter.com', 't.co'],
    'LinkedIn': ['linkedin.com', 'linkedin.in'],
}

def get_collection_name(domain):
    for platform, domains in social_media_domains.items():
        if any(d in domain for d in domains):
            return platform
    return 'Other'

async def search_google(query: str, page: int = Query(1, alias="page"), from_date: str = None, to_date: str = None, time_range: str = None):
    search_url = "https://www.googleapis.com/customsearch/v1"
    start_index = (page - 1) * 10 + 1
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "start": start_index,
    }
    if time_range == "custom" and from_date and to_date:
        start_date_str, end_date_str = get_date_range(time_range, from_date, to_date)
    elif time_range:
        start_date_str, end_date_str = get_date_range(time_range)
    else:
        start_date_str = end_date_str = None

    if start_date_str and end_date_str:
        params["sort"] = f"date:r:{start_date_str}:{end_date_str}"

    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        items = response.json().get('items', [])
        search_results = []
        for item in items:
            leader_name = query
            link = item.get('link')
            author = None
            headline = item.get('title')
            description = item.get('snippet')

            parsed_link = urlparse(link)
            domain = parsed_link.netloc

            collection_name = get_collection_name(domain)

            search_result = {
                "leader_name": leader_name,
                "link": link,
                "author": author,
                "headline": headline,
                "description": description
            }

            search_results.append((collection_name, search_result))

        if search_results:
            for collection_name, result in search_results:
                insert_search_results(collection_name, [result])

        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())
