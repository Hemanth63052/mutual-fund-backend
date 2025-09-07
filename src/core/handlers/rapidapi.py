from fastapi import status

from src.config import RapidAPIConfig
from src.core.schemas.rapidapi import CreateInvestmentModel, CreateInvestmentDatabaseModel, CreatePortfolio
from src.core.schemas.responses import SuccessResponseModel
from src.db.pg.handler import SQLHandler
from src.exceptions import MutualFundException


class RapidAPIHandler:

    def __init__(self, session):
        self.sql_handler = SQLHandler(session=session)

    @staticmethod
    async def get_headers() -> dict:
        """
        Get headers for RapidAPI requests
        :return: Dictionary of headers
        """
        if not RapidAPIConfig.RAPIDAPI_KEY:
            raise MutualFundException(
                message= "RapidAPI key not configured",
            )
        return {
            "X-RapidAPI-Key": RapidAPIConfig.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "example-rapidapi-host.p.rapidapi.com"
        }

    async def fetch_fund_families(self,):
        """Fetch available fund families from RapidAPI"""
        fund_families = await self.sql_handler.fetch_fund_families()
        return SuccessResponseModel(message="Fund families fetched successfully", data=fund_families)

    async def fetch_schemes_by_family(self, family_name: str):
        """
        Fetch open-ended schemes for a specific fund family
        :param family_name: Name of the fund family
        :return: List of open-ended schemes
        """
        schemes = await self.sql_handler.fetch_fund_family_schemes(family_name)
        if not schemes:
            return SuccessResponseModel(
                message=f"No schemes found for fund family: {family_name}",
                data=[]
            )
        final_schemes = []
        for scheme in schemes:
            scheme_data = {
                "scheme_code": scheme[0].scheme_code,
                "scheme_name": scheme[0].scheme_name,
                "fund_family": scheme[0].fund_family,
                "fund_type": scheme[0].fund_type,
                "nav": scheme[0].nav_history[-1].nav if scheme[0].nav_history else None,
                "date": scheme[0].nav_history[-1].updated_at if scheme[0].nav_history else None,

            }
            final_schemes.append(scheme_data)
        return SuccessResponseModel(message="Schemes fetched successfully", data=final_schemes)

    async def fetch_nav_by_scheme_code(self, scheme_code: str):
        """
        Fetch current NAV for a specific scheme using RapidAPI
        :param scheme_code: Scheme code of the mutual fund
        :return: Current NAV value or None if not found
        """
        nav = await self.sql_handler.fetch_nav_by_scheme_code(scheme_code)
        if nav is not None:
            return SuccessResponseModel(message="NAV fetched successfully", data=nav)

        raise MutualFundException(message="NAV not found for the given scheme code",
                                  data=[],
                                  code=status.HTTP_404_NOT_FOUND)


    async def create_investment(self, user_id: str, request_data: CreateInvestmentModel):
        """
        Create a new investment for a user
        :param user_id: ID of the user making the investment
        :param request_data: Details of the investment to be created
        :return: Details of the created investment
        """
        # Fetch the fund scheme by scheme code
        fund_scheme = await self.sql_handler.fetch_fund_scheme_by_id(request_data.scheme_id)
        if not fund_scheme:
            raise MutualFundException(message="Fund scheme not found for the given scheme code",
                                      code=status.HTTP_404_NOT_FOUND)

        if not request_data.portfolio_id:
            request_data.portfolio_id = await self.sql_handler.upsert_portfolio(user_id=user_id)

        # Create the investment record
        create_investment_schema = CreateInvestmentDatabaseModel(
            portfolio_id=str(request_data.portfolio_id),
            scheme_id=str(fund_scheme.id),
            amount=request_data.amount,
            units=request_data.amount / fund_scheme.nav_history[-1].nav if fund_scheme.nav_history else 0,
            purchased_nav=fund_scheme.nav_history[-1].nav if fund_scheme.nav_history else 0
        )
        await self.sql_handler.create_investment(data=create_investment_schema)
        return SuccessResponseModel(message="Investment created successfully", data=create_investment_schema.model_dump())

    # async def fetch_user_portfolio(self, user_id: str):
    #     """
    #     Fetch the portfolio of a user by user ID.
    #
    #     :param user_id: The ID of the user to fetch the portfolio for.
    #     :return: User portfolio details if found.
    #     """
    #     portfolio = await self.sql_handler.fetch_portfolio_by_user_id(user_id=user_id)
    #     return SuccessResponseModel(
    #         message="User portfolio fetched successfully",
    #         data={"portfolio": portfolio}
    #     )

    # async def create_user_portfolio(self, user_id: str, create_portfolio: CreatePortfolio):
    #     """
    #     Create a default portfolio for a user by user ID.
    #
    #     :param user_id: The ID of the user to create the portfolio for.
    #     :param create_portfolio: Data to create a new portfolio.
    #     :return: Confirmation message of portfolio creation.
    #     """
    #     portfolio_status, portfolio_id = await self.sql_handler.create_user_portfolio(user_id=user_id,
    #                                                                                   portfolio_data=create_portfolio)
    #     if not portfolio_status:
    #         raise MutualFundException(message="Portfolio already exists for the user.",
    #                                   code=status.HTTP_400_BAD_REQUEST)
    #     return SuccessResponseModel(
    #         message="User portfolio created successfully",
    #         data={"portfolio_id": portfolio_id}
    #     )

    async def fetch_investments_by_user_id(self, user_id: str):
        """
        Fetch all investments for a given portfolio ID.
        :param user_id: The ID of the user to fetch investments for.
        :return: List of investments if found.

        """
        investments = await self.sql_handler.fetch_investments_by_user_id(user_id=user_id)
        return SuccessResponseModel(
            message="Investments fetched successfully",
            data=investments
        )

    # async def fetch_investments_by_portfolio_id(self, portfolio_id: str):
    #     """
    #     Fetch all investments for a given portfolio ID.
    #     :param portfolio_id: The ID of the portfolio_id to fetch investments for.
    #     :return: List of investments if found.
    #     """
    #     investments = await self.sql_handler.fetch_investments_by_portfolio_id(portfolio_id=portfolio_id)
    #     return SuccessResponseModel(
    #         message="Investments fetched successfully",
    #         data={"investments": investments}
    #     )

    async def get_portfolio_summary(self, user_id: str):
        """
        Fetch portfolio summary for a given user ID.

        :param user_id: The ID of the user to fetch portfolio summary for.
        :return: Portfolio summary if found.
        """
        portfolio_summary = await self.sql_handler.get_portfolio_summary(user_id=user_id)
        if not portfolio_summary:
            portfolio_summary =  {
                'total_amount': 0.0,
                'total_value': 0.0,
                'gain_loss': 0.0,
                'returns_pct': 0.0,
                'total_investments': 0
            }
        else:
            portfolio_summary = portfolio_summary[0]
            portfolio_summary =  {
                'total_amount': round(float(portfolio_summary['total_amount']), 2),
                'total_value': round(float(portfolio_summary['total_value']), 2),
                'gain_loss': round(float(portfolio_summary['gain_loss']), 2),
                'returns_pct': round(float(portfolio_summary['returns_pct']), 2),
                'total_investments': int(portfolio_summary['total_investments'])
            }

        return SuccessResponseModel(
            message="Portfolio summary fetched successfully",
            data=portfolio_summary
        )
