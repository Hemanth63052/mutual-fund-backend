import datetime
from typing import Generator

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import TIMESTAMP, MetaData, create_engine

from src.config import SQLConfig
from src.logging import logger


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


    def create_default_dependencies(self, _engine, metadata: MetaData):
        # if not database_exists(str(_engine.url)):
        #     create_database(str(_engine.url))
        self.create_database()

        metadata.create_all(_engine, checkfirst=True)

    @staticmethod
    def create_database():
        """Create the database if it doesn't exist."""
        try:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

            #connect to psycopg2 from postgres url
            url = SQLConfig.SQL_URL.replace('postgresql+psycopg2://', 'postgresql://').rstrip("/")+"/postgres"
            conn = psycopg2.connect(url)
            cursor = conn.cursor()
            # Set autocommit mode - this is crucial for CREATE DATABASE
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (SQLConfig.SQL_DATABASE,))
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f'CREATE DATABASE "{SQLConfig.SQL_DATABASE}"')
                logger.info(f"Database {SQLConfig.SQL_DATABASE} created successfully!")
            else:
                logger.info(f"Database {SQLConfig.SQL_DATABASE} already exists")

            cursor.close()
            conn.close()
            return True

        except psycopg2.Error as e:
            logger.error(f"Error creating database: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False


session_util = SessionUtil()

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    yield from session_util.get_session()
