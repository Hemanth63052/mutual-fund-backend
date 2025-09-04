import datetime
import uuid
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy.dialects.postgresql import UUID
from src.db.pg.sessions import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    email: Mapped[str] = MappedColumn(nullable=False, unique=True, index=True)
    first_name: Mapped[str] = MappedColumn(nullable=False, index=True)
    last_name: Mapped[str] = MappedColumn(nullable=False, index=True)
    password: Mapped[str] = MappedColumn(nullable=False)
    is_active: Mapped[bool] = MappedColumn(default=True, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True
    )
    updated_at: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
        index=True,
    )
    idx_all = Index(
        "idx_user_all",
        id,
        email,
        first_name,
        last_name,
        postgresql_using="btree",
    )
