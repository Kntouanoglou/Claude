from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routers.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Course-Builder", lifespan=lifespan)
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
