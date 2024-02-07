from pymongo import MongoClient
from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client.get_database('cluster0')  # Specify your database name
collection = db['search_results']  # Specify your collection name

def check_connection():
    try:
        client.admin.command('ismaster')
        print("Connected to MongoDB Atlas")
    except Exception as e:
        print(f"Failed to connect to MongoDB Atlas: {e}")

check_connection()