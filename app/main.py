
from fastapi import FastAPI
from app.routers.short_url import router

app = FastAPI()

app.include_router(router)
