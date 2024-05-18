import backoff
import httpx
import asyncio
from fastapi import HTTPException, Query
from app.config import API_KEY, CSE_ID
from app.repository.tbl_news import insert_search_results
from app.utility.date_utils import get_date_range
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime, timedelta, timezone
from app import app


# Cache dictionary to store cached results
cache = {}
CACHE_EXPIRATION_SECONDS = 300  # Cache expiration time (5 minutes)

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



def generate_cache_key(query, page_number, time_range, from_date, to_date):
    """Generate a unique cache key based on query parameters."""
    key = f"{query}_{page_number}_{time_range}_{from_date}_{to_date}"
    return hashlib.md5(key.encode()).hexdigest()

# @backoff.on_exception(
#     backoff.expo,
#     (httpx.HTTPError, httpx.RequestError),
#     max_tries=5,  # Define max number of tries
#     giveup=lambda e: e.response and e.response.status_code < 500
# )
async def fetch_search_results(client, query, page_number, API_KEY, CSE_ID, time_range, from_date, to_date):
    start_index = (page_number - 1) * 10 + 1
    # some issue with env will move this to env
    params = {
        "key": "AIzaSyAkJk6rhIvjKkRGQPy8H8YTBfC-yhdHOKs",
        "cx": "b6f1294e3216948a8",
        "q": query,
        "start": start_index,
    }

    if time_range == "Custom" and from_date and to_date:
        start_date_str, end_date_str = get_date_range(time_range, from_date, to_date)
    elif time_range:
        start_date_str, end_date_str = get_date_range(time_range)
    else:
        start_date_str = end_date_str = None

    if start_date_str and end_date_str:
        params["sort"] = f"date:r:{start_date_str}:{end_date_str}"

    response = await client.get("https://www.googleapis.com/customsearch/v1", params=params)
    response.raise_for_status()
    return response.json()

async def search_google(query: str, page: int = Query(1, alias="page"), from_date: str = None, to_date: str = None,
                        time_range: str = None, twitter_handle=None, facebook_id=None, instagram_id=None, youtube_id=None, extra_query= None):
    if not query:
        raise HTTPException(status_code=400, detail="The query parameter is required.")
    
    cache_key = generate_cache_key(query, page, time_range, from_date, to_date)

        # Check if the result is cached
    if cache_key in cache:
        cached_entry = cache[cache_key]
        print('Returning from Cache now')
        if cached_entry["expires_at"] > datetime.now(timezone.utc):
            return cached_entry["result"]

    print("First Time Fetching")   
        

    all_search_results = []
    tasks = []
    social_results = {'facebook': [], 'twitter': [], 'instagram': [], 'youtube': []}


    async with httpx.AsyncClient() as client:
        for page_number in range(1, page + 1):
            if extra_query:
                full_query = f"{query} {extra_query}"
            else:
                full_query = query    
            task = fetch_search_results(client, full_query, page_number, API_KEY, CSE_ID, time_range, from_date, to_date)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                print(f"An error occurred: {response}")
                continue  # Skip this response and continue with the next

            items = response.get('items', [])
            if items:
                search_results = create_search_result_array(query, items)    # Scrape content from the URLs
                await add_web_content(search_results)                
                if search_results:
                    all_search_results.extend(search_results)

        # Prepare for social media queries
        social_queries = {
            'facebook': f"site:https://www.facebook.com/{facebook_id}" if facebook_id else None,
            'twitter': f"site:https://twitter.com/{twitter_handle}" if twitter_handle else None,
            'instagram': f"site:https://www.instagram.com/{instagram_id}" if instagram_id else None,
            'youtube': f"site:https://www.youtube.com/{youtube_id}" if youtube_id else None
        }

        tasks_social = []
        
        for platform, social_query in social_queries.items():
            if social_query:
                task = fetch_search_results(client, social_query, 1, API_KEY, CSE_ID, None, None, None)
                tasks_social.append((platform, task))

        social_responses = await asyncio.gather(*[task[1] for task in tasks_social if task], return_exceptions=True)

        for i, response in enumerate(social_responses):
            platform = tasks_social[i][0]
            if isinstance(response, Exception):
                print(f"An error occurred in {platform} search: {response}")
                continue

            items = response.get('items', [])
            if items:
                social_results[platform].extend(create_search_result_array(query, items))

    result = {
        "status": True if all_search_results or any(social_results[plat] for plat in social_results) else False,
        "message": "Data fetched successfully" if all_search_results or any(social_results[plat] for plat in social_results) else "No data found",
        "data": all_search_results,
        **social_results
    }

    # Cache the result
    cache[cache_key] = {
        "result": result,
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=CACHE_EXPIRATION_SECONDS)
    }

    return result


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



async def scrape_content_from_url(url):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract the entire page content as text
        web_content = soup.get_text(separator=' ')
        return web_content


async def add_web_content(search_results):
    valid_results = [result for result in search_results if is_valid_url(result['url'])]
    tasks = [scrape_and_add_content(result) for result in valid_results]
    await asyncio.gather(*tasks)


async def scrape_and_add_content(result):
    try:
        content = await scrape_content_from_url(result['url'])
        result['web_content'] = content
    except Exception as e:
        print(f"Error scraping {result['url']}: {e}")
        result['web_content'] = None

def is_valid_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        return False
    if parsed_url.netloc == '':
        return False
    file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.zip', '.rar', '.7z', '.tar', '.gz']
    if any(url.lower().endswith(ext) for ext in file_extensions):
        return False
    return True        
