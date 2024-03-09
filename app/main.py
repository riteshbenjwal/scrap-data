from . import app
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search_router


from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request



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


@app.get("/")
def read_root():
    return {"Hello": "World"}

# Include the router
app.include_router(search_router.router)



@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.detail,
            "data": []
        },
    )
