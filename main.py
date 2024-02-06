from fastapi import FastAPI, HTTPException
import requests
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

app = FastAPI()

API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

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
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())
