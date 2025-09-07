from src.core.schemas.rapidapi import CreateInvestmentDatabaseModel, CreatePortfolio
from src.core.schemas.user import RegisterUser
from src.db.pg.queries import SQLQueries
from src.db.pg.ops import SQLOps
from src.db.pg.sql_schemas import Users, Portfolio, Investment, FundScheme, NavHistory


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

    async def fetch_user_by_id(self, user_id: str):
        """
        Fetch a user by their ID.

        :param user_id: The ID of the user to fetch.
        :return: The user object if found, None otherwise.
        """
        query = SQLQueries.fetch_user_by_id(user_id)
        result = await self.sql_ops.execute_query(query=query, first_result=True, json_result=True)
        return result

    async def fetch_fund_families(self):
        """
        Fetch all fund families.

        :return: A list of fund families.
        """
        query = SQLQueries.fetch_fund_families()
        result = await self.sql_ops.execute_query(query=query, json_result=True)
        return result

    async def fetch_fund_family_schemes(self, fund_family: str):
        """
        Fetch all fund families.
        :param fund_family: The fund family to filter schemes.
        :return: A list of fund families.
        """
        query = SQLQueries.fetch_schemes_by_family(fund_family=fund_family)
        result = await self.sql_ops.execute_query(query=query)
        return result

    async def fetch_nav_by_scheme_code(self, scheme_code: str):
        """
        Fetch NAV by scheme code.
        :param scheme_code: The scheme code to filter NAV.
        :return: A list of NAVs.
        """
        query = SQLQueries.fetch_nav_by_scheme_code(scheme_code=scheme_code)
        result = await self.sql_ops.execute_query(query=query, first_result=True, json_result=True)
        return result

    async def fetch_fund_scheme_by_id(self, fund_scheme_id: str):
        """
        Fetch a fund scheme by its ID.
        :param fund_scheme_id: The ID of the fund scheme to fetch.
        :return: The fund scheme object if found, None otherwise.
        """
        query = SQLQueries.fetch_fund_scheme_by_id(fund_scheme_id=fund_scheme_id)
        result = await self.sql_ops.execute_query(query=query, first_result=True)
        return result

    async def upsert_portfolio(self, user_id: str):
        """
        Upsert a portfolio record in the database.

        :param user_id: The ID of the user to whom the portfolio belongs.
        :return: The result of the executed upsert query.
        """
        portfolio_user_query = SQLQueries.fetch_portfolio_by_user_id(user_id)
        if portfolio_user := await self.sql_ops.execute_query(query=portfolio_user_query, first_result=True):
            return portfolio_user.id
        new_portfolio = {
            "user_id": user_id,
            "name": "Default Portfolio",
            "description": "This is the default portfolio.",
        }
        portfolio = self.sql_ops.insert_one(data=new_portfolio, model=Portfolio)
        return portfolio.id

    async def fetch_portfolio_by_user_id(self, user_id: str):
        """
        Fetch a portfolio by its ID.

        :param user_id: The ID of the user to whom the portfolio belongs.
        :return: The portfolio object if found, None otherwise.
        """
        query = SQLQueries.fetch_portfolio_by_user_id(user_id)
        result = await self.sql_ops.execute_query(query=query, json_result=True)
        return result

    async def create_investment(self, data:CreateInvestmentDatabaseModel):
        """
        Create a new investment record in the database.

        :param data: The data for the new investment.
        :return: The result of the executed insert query.

        """
        return self.sql_ops.insert_one(data=data.model_dump(), model=Investment)

    async def fetch_portfolios_by_id(self, portfolio_id: str):
        """
        Fetch all investments for a given portfolio ID.

        :param portfolio_id: The ID of the portfolio to fetch investments for.
        :return: A list of investments associated with the portfolio.
        """
        query = SQLQueries.fetch_portfolios_by_id(portfolio_id)
        result = await self.sql_ops.execute_query(query=query, json_result=True)
        return result

    async def create_user_portfolio(self, user_id: str, portfolio_data: CreatePortfolio):
        """
        Create a default portfolio for a user if none exists.

        :param user_id: The ID of the user to create the portfolio for.\
        :param portfolio_data: Data to create a new portfolio.
        :return: The result of the executed insert query.
        """
        portfolio_user_query = SQLQueries.fetch_portfolio_by_name(user_id)
        if await self.sql_ops.execute_query(query=portfolio_user_query, first_result=True):
            return False, "Portfolio with the same name already exists."
        portfolio_data = portfolio_data.model_dump()
        portfolio_data['user_id'] = str(user_id)
        portfolio = self.sql_ops.insert_one(data=portfolio_data, model=Portfolio)
        return True, portfolio.id

    async def fetch_investments_by_user_id(self, user_id: str):
        """
        Fetch all investments for a given user ID.
        :param user_id: The ID of the user to fetch investments for.
        :return: A list of investments associated with the user.
        """
        query = SQLQueries.fetch_investments_by_user_id(user_id)
        result = await self.sql_ops.execute_query(query=query, json_result=True)
        return result

    # async def fetch_investments_by_portfolio_id(self, portfolio_id: str):
    #     """
    #     Fetch all investments for a given portfolio ID.
    #     :param portfolio_id: The ID of the portfolio to fetch investments for.
    #     :return: A list of investments associated with the portfolio.
    #     """
    #     query = SQLQueries.fetch_investments_by_portfolio_id(portfolio_id)
    #     result = await self.sql_ops.execute_query(query=query, json_result=True)
    #     return result


    async def upsert_fund_schemes(self, fund_schemes: dict):
        """
        Upsert multiple fund scheme records in the database.

        :param fund_schemes: A list of dictionaries containing fund scheme data.
        :return: The result of the executed upsert query.
        """
        return await self.sql_ops.upsert_query(data=fund_schemes, model=FundScheme, conflict_columns=['scheme_code'])

    async def upsert_nav_history(self, nav_histories: dict):
        """
        Upsert multiple NAV history records in the database.

        :param nav_histories: A list of dictionaries containing NAV history data.
        :return: The result of the executed upsert query.
        """
        return await self.sql_ops.upsert_query(data=nav_histories, model=NavHistory, conflict_columns=["scheme_id"])

    async def get_portfolio_summary(self, user_id: str):
        """
        Fetch portfolio summary for a given user ID.
        :param user_id: The ID of the user to fetch portfolio summary for.
        :return: A list of portfolio summaries associated with the user.
        """
        query = await SQLQueries.get_portfolio_summary_query(user_id)
        result = await self.sql_ops.execute_query(query=query, json_result=True)
        return result

    async def bulk_upsert_fund_schemes(self, fund_schemes: list[dict]):
        """
        Bulk upsert multiple fund scheme records in the database.

        :param fund_schemes: A list of dictionaries containing fund scheme data.
        :return: A dictionary mapping scheme codes to their corresponding IDs.
        """
        return await self.sql_ops.bulk_upsert_fund_schemes(data_list=fund_schemes, model=FundScheme, conflict_columns=['scheme_code'])

    async def bulk_upsert_nav_history(self, nav_histories: list[dict]):
        """
        Bulk upsert multiple NAV history records in the database.
        """

        return await self.sql_ops.bulk_upsert_nav_history(data_list=nav_histories, model=NavHistory, conflict_columns=["scheme_id"])

