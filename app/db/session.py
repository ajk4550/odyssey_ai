from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from core.config import settings

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
