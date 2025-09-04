import datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.db.pg.sql_schemas import Users


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
        pass
