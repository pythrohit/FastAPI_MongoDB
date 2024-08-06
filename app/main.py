from fastapi import FastAPI, HTTPException
from app.cores.config import custom_http_exception_handler
from app.routers import user, blog
from app.cores.database import lifespan

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(blog.router, prefix="/blogs", tags=["blogs"])

# Exception handler
app.add_exception_handler(HTTPException, custom_http_exception_handler)


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}
