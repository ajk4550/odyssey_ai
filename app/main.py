from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router
from db.init_db import init_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

