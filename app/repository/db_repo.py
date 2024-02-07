from pymongo import MongoClient
from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client.get_database('cluster0')
collection = db['search_results'] 


def insert_search_results(search_results):
    """
    Inserts search results into the MongoDB collection.
    """
    if search_results:
        collection.insert_many(search_results)
