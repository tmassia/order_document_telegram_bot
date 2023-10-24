from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    return create_engine(url=url, echo_pool=True, encoding='utf-8', pool_pre_ping=True)


def proceed_schema(session: AsyncSession, metadata) -> None:
    with session.begin():
        session.run_sync(metadata.create_all())


def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession)
