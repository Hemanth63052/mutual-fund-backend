import datetime
import uuid

from sqlalchemy import Index, ForeignKey
from sqlalchemy.orm import Mapped, MappedColumn, relationship
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
    phone_number: Mapped[str] = MappedColumn(nullable=True, unique=True, index=True)
    address: Mapped[str] = MappedColumn(nullable=True)
    password: Mapped[str] = MappedColumn(nullable=False)
    is_active: Mapped[bool] = MappedColumn(default=True, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True
    )
    updated_at: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
        index=True,
    )
    portfolios = relationship("Portfolio", back_populates="user")
    idx_all = Index(
        "idx_user_all",
        id,
        email,
        first_name,
        last_name,
        postgresql_using="btree",
    )


class Portfolio(Base):
    __tablename__ = "portfolios"

    id : Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id : Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = MappedColumn(nullable=False, index=True)
    description: Mapped[str] = MappedColumn(nullable=True)
    created_at : Mapped[datetime.datetime] = MappedColumn(
        default=datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True
    )
    updated_at : Mapped[datetime.datetime] = MappedColumn(
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
        index=True,
    )

    user = relationship("Users", back_populates="portfolios")
    investments = relationship("Investment", back_populates="portfolio")


class FundScheme(Base):
    __tablename__ = "fund_schemes"

    id: Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    scheme_code: Mapped[str] = MappedColumn(unique=True, index=True, nullable=False)
    scheme_name: Mapped[str] = MappedColumn(nullable=False)
    fund_family: Mapped[str] = MappedColumn(nullable=False)
    fund_type: Mapped[str] = MappedColumn(nullable=False)
    created_at: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True)
    updated_at: Mapped[datetime.datetime] = MappedColumn(
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
        index=True,
    )
    investments = relationship("Investment", back_populates="fund_scheme")

    nav_history = relationship("NavHistory", back_populates="fund_scheme")



class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    portfolio_id: Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheme_id: Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True),
        ForeignKey("fund_schemes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = MappedColumn(nullable=False)  # Investment amount
    units: Mapped[float] = MappedColumn(nullable=False)  # Number of units purchased
    purchased_nav: Mapped[float] = MappedColumn(nullable=False)  # NAV at time of purchase
    # current_nav: Mapped[float] = MappedColumn(nullable=False)  # Current NAV
    # current_value: Mapped[float] = MappedColumn(nullable=False)  # Current value (units * current_nav)
    investment_date: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc))
    is_active: Mapped[bool] = MappedColumn(default=True, nullable=False)
    updated_at: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc), nullable=False)

    portfolio = relationship("Portfolio", back_populates="investments")
    fund_scheme = relationship("FundScheme", back_populates="investments")


class NavHistory(Base):
    __tablename__ = "nav_history"
    id: Mapped[uuid.UUID] = MappedColumn(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    scheme_id = MappedColumn(UUID(as_uuid=True), ForeignKey("fund_schemes.id", ondelete="CASCADE"), unique = True, nullable=False, index=True)
    nav: Mapped[float] = MappedColumn(nullable=False)
    updated_at: Mapped[datetime.datetime] = MappedColumn(default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc), nullable=False)

    fund_scheme = relationship("FundScheme", back_populates="nav_history")

# from sqlalchemy import create_engine
# engine = create_engine("")
# Base.metadata.create_all(engine)
