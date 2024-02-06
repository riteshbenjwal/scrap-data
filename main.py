from fastapi import FastAPI, HTTPException, Response
import requests
from dotenv import load_dotenv
import os
from pymongo import MongoClient
# Load .env file
load_dotenv()

app = FastAPI()

API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")
MONGODB_URI = os.getenv("MONGODB_URI")

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)

# Check if connected to MongoDB Atlas
try:
    client.admin.command('ismaster')
    print("Connected to MongoDB Atlas")
except Exception as e:
    print("Failed to connect to MongoDB Atlas:", e)

db = client.get_database('cluster0')  
collection = db['search_results'] 


@app.get("/search")
def search_google(query: str, start_date: str = None, end_date: str = None):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
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
            collection.insert_many(search_results)

        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())
