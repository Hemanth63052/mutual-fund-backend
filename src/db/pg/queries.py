from sqlalchemy import select, func, case, text
from sqlalchemy.orm import joinedload

from src.db.pg.sql_schemas import Users, FundScheme, Portfolio, Investment, NavHistory


class SQLQueries:
    """
    This class contains SQL queries for user management operations.
    It is used to interact with the PostgreSQL database.
    """

    @staticmethod
    def check_user_with_email(email: str) -> select:
        """
        SQL query to check if a user exists with the given email.

        :arg.
            email (str): The email of the user to check.
        :return:
            select: SQLAlchemy select query to check user existence.
        """
        return select(Users).where(Users.email == email)

    @staticmethod
    def fetch_user_by_id(user_id: str) -> select:
        """
        SQL query to fetch a user by their ID.

        :arg.
            user_id (str): The ID of the user to fetch.
        :return:
            select: SQLAlchemy select query to fetch the user.
        """
        return select(*Users.__table__.columns).select_from(Users).where(Users.id == user_id)

    @staticmethod
    def fetch_fund_families():
        """
        SQL query to fetch all fund families.

        :return:
            select: SQLAlchemy select query to fetch all fund families.
        """
        return select(
            FundScheme.id,
            FundScheme.fund_family,
            FundScheme.scheme_code,
            FundScheme.scheme_name,
            FundScheme.fund_type,
            NavHistory.nav,
            NavHistory.updated_at,
        ).join(NavHistory, FundScheme.id == NavHistory.scheme_id).order_by(FundScheme.fund_family)

    @staticmethod
    def fetch_schemes_by_family(fund_family: str):
        """
        SQL query to fetch schemes by fund family.

        :arg.
            fund_family (str): The fund family to filter schemes.
        :return:
            select: SQLAlchemy select query to fetch schemes by fund family.
        """
        return select(FundScheme).where(FundScheme.fund_family == fund_family).order_by(FundScheme.scheme_name)

    @staticmethod
    def fetch_nav_by_scheme_code(scheme_code: str):
        """
        SQL query to fetch NAV by scheme code.

        :arg.
            scheme_code (str): The scheme code to filter NAV.
        :return:
            select: SQLAlchemy select query to fetch NAV by scheme code.
        """
        return select(*NavHistory.__table__.columns).join(FundScheme, FundScheme.id == NavHistory.scheme_id).where(
            FundScheme.scheme_code == scheme_code).order_by(NavHistory.updated_at.desc())

    @staticmethod
    def fetch_fund_scheme_by_id(fund_scheme_id: str):
        """
        SQL query to fetch a fund scheme by its ID.

        :arg.
            fund_scheme_id (str): The ID of the fund scheme to fetch.
        :return:
            select: SQLAlchemy select query to fetch the fund scheme.
        """
        return select(FundScheme).options(joinedload(FundScheme.nav_history)).where(FundScheme.id == fund_scheme_id)

    @staticmethod
    def fetch_portfolio_by_user_id(user_id: str):
        """
        SQL query to fetch a portfolio by its ID.

        :arg.
            user_id (str): The ID of the user to whom the portfolio belongs.
        :return:
            select: SQLAlchemy select query to fetch the portfolio.
        """

        return select(Portfolio).options(joinedload(Portfolio.user)).where(Portfolio.user_id == user_id)

    @staticmethod
    def fetch_portfolios_by_id(portfolio_id: str):
        """
        SQL query to fetch investments by portfolio ID.

        :arg.
            portfolio_id (str): The ID of the portfolio to fetch investments for.
        :return:
            select: SQLAlchemy select query to fetch investments by portfolio ID.
        """

        return select(Portfolio).where(Portfolio.id == portfolio_id)

    @staticmethod
    def fetch_portfolio_by_name(portfolio_name: str):
        """
        SQL query to fetch a portfolio by its ID.

        :arg.
            portfolio_name (str): The portfolio_name of the portfolio to fetch.
        :return:
            select: SQLAlchemy select query to fetch the portfolio.
        """

        return select(Portfolio).where(Portfolio.name == portfolio_name)

    @staticmethod
    def fetch_investments_by_user_id(user_id: str):
        """
        SQL query to fetch investments by user ID.

        :arg.
            user_id (str): The ID of the user to fetch investments for.
        :return:
            select: SQLAlchemy select query to fetch investments by user ID.
        """

        return select(Investment.id,
                      Investment.amount,
                      Investment.units,
                      Investment.purchased_nav,
                      Investment.updated_at,
                      FundScheme.scheme_name,
                      FundScheme.scheme_code,
                      FundScheme.fund_family,
                      FundScheme.fund_type,
                      (Investment.units * NavHistory.nav).label('current_value'),
                      (Investment.units * NavHistory.nav - Investment.amount).label('gain_loss'),
                      case(
                            (Investment.amount > 0,
                             (Investment.units * NavHistory.nav - Investment.amount) / Investment.amount * 100),
                          else_=0
                      ).label('returns_pct')
                    ).join(Portfolio, Investment.portfolio_id == Portfolio.id
                    ).join(FundScheme, Investment.scheme_id == FundScheme.id
                    ).join(NavHistory, FundScheme.id == NavHistory.scheme_id
                    ).where(
            Portfolio.user_id == user_id,
            Investment.is_active == True).order_by( Investment.updated_at.desc())

    @staticmethod
    def fetch_investments_by_portfolio_id(portfolio_id: str):
        """
        SQL query to fetch investments by portfolio ID.

        :arg.
            portfolio_id (str): The ID of the portfolio to fetch investments for.
        :return:
            select: SQLAlchemy select query to fetch investments by portfolio ID.
        """

        return select(Investment).options(joinedload(Investment.fund_scheme), joinedload(Investment.portfolio)).where(
            Investment.portfolio_id == portfolio_id)


    @staticmethod
    async def get_portfolio_summary_query(user_id):
        """
        Returns SQLAlchemy select query for portfolio summary
        Note: Rounding will be done in Python after getting results
        """
        query = (select(
            func.coalesce(func.sum(Investment.amount), 0).label('total_amount'),
            func.coalesce(func.sum(Investment.units * NavHistory.nav), 0).label('total_value'),
            func.coalesce(func.sum((Investment.units * NavHistory.nav) - Investment.amount), 0).label('gain_loss'),
            case(
                (func.sum(Investment.amount) > 0,
                 (func.sum((Investment.units * NavHistory.nav) - Investment.amount) / func.sum(Investment.amount) * 100)
                 ),
                else_=0
            ).label('returns_pct'),
            func.count(Investment.id).label('total_investments')
        ).select_from(Investment)
        .join(Portfolio, Investment.portfolio_id == Portfolio.id)
        .join(FundScheme, Investment.scheme_id == FundScheme.id)
        .join(NavHistory, FundScheme.id == NavHistory.scheme_id)
        .where(
            Portfolio.user_id == user_id,
            Investment.is_active == True
        ))

        return query
