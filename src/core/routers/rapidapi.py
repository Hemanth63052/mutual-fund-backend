from fastapi import APIRouter, Depends

from src.core.handlers.auth import ModuleAuthenticationHandler
from src.core.handlers.rapidapi import RapidAPIHandler
from src.core.schemas.rapidapi import CreateInvestmentModel
from src.db.pg.sessions import get_db

rapidapi_router = APIRouter()


@rapidapi_router.get("/fund-families")
async def get_fund_families(session=Depends(get_db)):
    """
    Endpoint to fetch fund families from RapidAPI.
    This is a placeholder implementation and should be replaced with actual logic to call RapidAPI.
    """
    return await RapidAPIHandler(session=session).fetch_fund_families()

@rapidapi_router.get("fund-families/{family_name}/schemes")
async def get_schemes_by_family(family_fund: str, session=Depends(get_db)):
    """
    Endpoint to fetch schemes by fund family from RapidAPI.
    This is a placeholder implementation and should be replaced with actual logic to call RapidAPI.
    """
    return await RapidAPIHandler(session=session).fetch_schemes_by_family(family_name=family_fund)

@rapidapi_router.get("fund-families/family/{scheme_code}/nav")
async def get_nav_by_scheme_code(scheme_code: str, session=Depends(get_db)):
    """
    Endpoint to fetch NAV by scheme code from RapidAPI.
    This is a placeholder implementation and should be replaced with actual logic to call RapidAPI.
    """
    return await RapidAPIHandler(session=session).fetch_nav_by_scheme_code(scheme_code=scheme_code)

@rapidapi_router.post("/investment")
async def create_investment(create_investment_schema:CreateInvestmentModel, session=Depends(get_db), user=Depends(ModuleAuthenticationHandler.get_current_user)):
    """
    Endpoint to create an investment.
    This is a placeholder implementation and should be replaced with actual logic to create an investment.
    """
    return await RapidAPIHandler(session=session).create_investment(user_id=user.id, request_data=create_investment_schema)

@rapidapi_router.get("/investments")
async def get_investment_history(session=Depends(get_db), user=Depends(ModuleAuthenticationHandler.get_current_user)):
    """
    Endpoint to fetch investment history.
    This is a placeholder implementation and should be replaced with actual logic to fetch investment history.
    """
    return await RapidAPIHandler(session=session).fetch_investments_by_user_id(user_id=user.id)

@rapidapi_router.get("/investment/{portfolio_id}/history")
async def get_investment_history_by_portfolio(portfolio_id: str, session=Depends(get_db)):
    """
    Endpoint to fetch investment history by portfolio ID.
    This is a placeholder implementation and should be replaced with actual logic to fetch investment history by portfolio ID.
    """
    return await RapidAPIHandler(session=session).fetch_investments_by_portfolio_id(portfolio_id=portfolio_id)

@rapidapi_router.get("/portfolios")
async def get_portfolios(session=Depends(get_db), user=Depends(ModuleAuthenticationHandler.get_current_user)):
    """
    Endpoint to fetch portfolios.
    This is a placeholder implementation and should be replaced with actual logic to fetch portfolios.
    """
    return await RapidAPIHandler(session=session).fetch_user_portfolio(user_id=user.id)
