import requests
from fastapi import HTTPException, Query
from app.config import API_KEY, CSE_ID
from app.repository.tbl_news import insert_search_results
from app.utility.date_utils import get_date_range
from urllib.parse import urlparse

category_ids = {
    "facebook": 1,
    "instagram": 2,
    "twitter": 3,
    "linkedin": 4,
    "other": 5
}

def getCategoryId(name):
    return category_ids.get(name, category_ids["other"])

social_media_domains = {
    'instagram': ['instagram.com', 'instagr.am', 'help.instagram.com', 'm.instagram.com', 'ig.me', 'applink.instagram.com', 'call.instagram.com'],
    'facebook': ['facebook.com', 'fb.com', 'messenger.com'],
    'twitter': ['twitter.com', 't.co'],
    'linkedin': ['linkedin.com', 'linkedin.in'],
}

def get_category_matched_id(domain):
    for platform, domains in social_media_domains.items():
        if any(d in domain for d in domains):
            return getCategoryId(platform)
    return getCategoryId('other')

async def search_google(query: str, page: int = Query(1, alias="page"), from_date: str = None, to_date: str = None, time_range: str = None):
    if not query:
        raise HTTPException(status_code=400, detail="The leader_name parameter is required.")

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
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status() 
        items = response.json().get('items', [])
        search_results = create_search_result_array(query,items)
        if search_results:
            # insert_search_results(search_results)
            return {
                "status": True,
                "message": "Data fetched successfully",
                "data": search_results
            }       
            
         #return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {
            "status": False,
            "message": f"HTTP error occurred: {http_err}",
            "data": []
        }

    except  Exception as err:
        return {
            "status": False,
            "message": f"An error occurred: {err}",
            "data": []
        }   

def create_search_result_array(query,items):
    search_results = []
    for item in items: 
        leader_name = query
        url = item.get('link')
        title = item.get('title')
        description = item.get('snippet')
        # Default values
        author = None
        published_at = None

        parsed_link = urlparse(url)
        domain = parsed_link.netloc

        category_id = get_category_matched_id(domain)

        # Attempt to extract author
        if item.get('author'):
            author = item.get('author')
        else:
            # Check metatags for author
            for metatag in item.get("pagemap", {}).get("metatags", []):
                if "article:author" in metatag:
                    author = metatag["article:author"]
                    break  # Stop looking if we've found an author

        # Attempt to extract published_at
        if item.get('publishedAt'):
            published_at = item.get('publishedAt')
        else:
            # Check metatags for published time
            for metatag in item.get("pagemap", {}).get("metatags", []):
                if "article:published_time" in metatag:
                    published_at = metatag["article:published_time"]
                    break  # Stop looking if we've found a published time
        
        search_result = {
            "url": url,
            "author": author,
            "leader_name": leader_name,
            "title": title,
            "description": description,
            "published_at": published_at,
            "category":category_id

        }
        search_results.append(search_result)
   
   
    return search_results    