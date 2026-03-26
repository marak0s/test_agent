from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from onlycuts.app.db.base import Base
from onlycuts.app.db.models import Channel


def test_repository_smoke_sqlite() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[Channel.__table__])
    Session = sessionmaker(bind=engine)
    with Session() as session:
        channel = Channel(code="OnlyAiOps", name="OnlyAiOps")
        session.add(channel)
        session.commit()
        assert channel.id is not None
