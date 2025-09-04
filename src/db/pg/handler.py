from src.core.schemas.user import RegisterUser
from src.db.pg.queries import SQLQueries
from src.db.pg.ops import SQLOps
from src.db.pg.sql_schemas import Users


class SQLHandler:
    """
    SQLHandler is a base class for handling SQL operations.
    It provides methods to execute SQL queries and manage database connections.
    """

    def __init__(self, session):
        self.sql_ops = SQLOps(session)

    async def check_user_exists_by_mail(self, email: str):
        """
        Check if a user exists with the given email.

        :param email: The email of the user to check.
        :return: True if the user exists, False otherwise.
        """
        query = SQLQueries.check_user_with_email(email)
        result = await self.sql_ops.execute_query(query=query, first_result=True)
        return result

    async def insert_new_user(self, new_user:RegisterUser):
        """
        Insert a new user into the database.

        :param new_user: A dictionary containing user data.
        :return: The result of the insert operation.
        """
        return self.sql_ops.insert_one(new_user.model_dump(), model=Users)

