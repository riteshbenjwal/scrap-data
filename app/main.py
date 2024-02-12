from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search_router

app = FastAPI()

allowed_origins = [
    "*" 
]

# Add CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # List of allowed origins
    allow_credentials=True,  # Whether to support credentials (cookies, Authorization headers, etc.)
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the router
app.include_router(search_router.router)
