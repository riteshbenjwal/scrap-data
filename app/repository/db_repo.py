from pymongo import MongoClient
from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client.get_database('cluster0')

def insert_search_results(collection_name, search_results):
    """
    Inserts search results into the specified MongoDB collection.
    """
    if search_results:
        collection = db[collection_name]
        collection.insert_many(search_results)
