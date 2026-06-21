from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = None
_async_session_maker = None

Base = declarative_base()


def init_engine(database_url: str = None):
    global engine, _async_session_maker
    url = database_url or settings.DATABASE_URL
    engine = create_async_engine(url, echo=settings.DEBUG)
    _async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return engine


def get_session_maker():
    return _async_session_maker


async def init_db():
    global engine
    if engine is None:
        init_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    global engine
    if engine:
        await engine.dispose()
        engine = None