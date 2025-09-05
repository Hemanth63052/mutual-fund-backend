from pydantic import BaseModel


class CreateInvestmentModel(BaseModel):
    scheme_id: str
    amount: float
    portfolio_id: str | None = None

class CreateInvestmentDatabaseModel(CreateInvestmentModel):
    units: float
    purchased_nav: float



class CreatePortfolio(BaseModel):
    """
    Schema for creating a new portfolio.
    This schema is used to validate the data when a new portfolio is created.
    """
    name: str
    description: str | None = None
