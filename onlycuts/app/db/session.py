from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from onlycuts.app.config.settings import settings


@lru_cache
def get_engine():
    return create_engine(settings.database_url, future=True)


SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)
