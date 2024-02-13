import requests
from fastapi import HTTPException, Query
from app.config import API_KEY, CSE_ID
from typing import List


async def search_youtube_service(query: str, page_token: str = None, max_results: int = 10, order: str = "relevance", time_range: str = None, from_date: str = None, to_date: str = None):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": max_results,
        "order": order,
        "key": API_KEY,
        "type": "video",
    }

    # Handle date range
    if time_range:
        start_date_str, end_date_str = get_date_range(time_range, from_date, to_date)
        if start_date_str and end_date_str:
            # The YouTube API requires dates in RFC 3339 format, so conversion may be necessary
            published_after = f"{start_date_str}T00:00:00Z"
            published_before = f"{end_date_str}T23:59:59Z"
            params["publishedAfter"] = published_after
            params["publishedBefore"] = published_before

    if page_token:
        params["pageToken"] = page_token

    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        # items = response.json().get('items', [])
      return response.json()
        # search_results = []
        # for item in items:
        #     video_id = item['id']['videoId']
        #     snippet = item['snippet']
        #     search_result = {
        #         "video_id": video_id,
        #         "title": snippet['title'],
        #         "description": snippet['description'],
        #         "published_at": snippet['publishedAt'],
        #         "thumbnails": snippet['thumbnails'],
        #         "channel_title": snippet['channelTitle'],
        #     }
        #     search_results.append(search_result)

        # return {"items": search_results, "nextPageToken": response.json().get('nextPageToken')}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())



def fetch_video_details(video_ids: List[str]):
    video_details_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": ','.join(video_ids),
        "key": API_KEY
    }
    response = requests.get(video_details_url, params=params)
    if response.status_code == 200:
        return response.json()['items']
    else:
        raise Exception("Failed to fetch video details")
