import datetime
from typing import Generator

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import TIMESTAMP, MetaData, create_engine

from src.config import SQLConfig


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """

    type_annotation_map = {datetime.datetime: TIMESTAMP(timezone=True)}


class SessionUtil:
    def __init__(self):
        self.user_engines = {}
        self.sessionmakers = {}

    def get_session(self, database: str = SQLConfig.SQL_DATABASE, metadata: MetaData = None) -> Generator[Session, None, None]:
        self._get_engine(database=database, metadata=metadata)
        sessionmaker_ = self.sessionmakers[database]
        with sessionmaker_() as session:
            yield session

    def _get_engine(self, database: str = SQLConfig.SQL_DATABASE, metadata: MetaData = None):
        if database not in self.user_engines:
            engine = create_engine(
                f"{SQLConfig.SQL_URL}/{SQLConfig.SQL_DATABASE}",
                connect_args={"connect_timeout": 10000},
                pool_size=1,
                pool_pre_ping=True,
                future=True,
            )
            self.user_engines[database] = engine

            self.sessionmakers[database] = sessionmaker(
                bind=engine,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            self.create_default_dependencies(
                _engine=self.user_engines[database],
                metadata=metadata or Base.metadata
            )
        return self.user_engines[database]

    @staticmethod
    def create_default_dependencies(_engine, metadata: MetaData):
        # if not database_exists(str(_engine.url)):
        #     create_database(str(_engine.url))

        metadata.create_all(_engine, checkfirst=True)


session_util = SessionUtil()

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    yield from session_util.get_session()
