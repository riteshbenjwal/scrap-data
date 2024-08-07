from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")
MONGODB_URI = os.getenv("MONGODB_URI")

print('API_KEY ==>',API_KEY)
print('CSE_ID ==>',CSE_ID)
print('MONGODB_URI ==>',MONGODB_URI)