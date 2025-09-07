import datetime

import httpx
from sqlalchemy.orm import Session
from src.logging import logger
from src.config import RapidAPIConfig
from src.db.pg.handler import SQLHandler
from src.db.pg.sessions import get_db


class SchedulerHandler:
    async def update_all_portfolios(self):
        """
        Fetch latest fund schemes from RapidAPI and update Postgres.
        This function runs once per schedule (APScheduler handles intervals).
        """
        try:
            logger.info("Inside scheduler to update portfolios")
            db: Session = next(get_db())
            sql_handler = SQLHandler(session=db)

            fund_schemes = await self.fetch_fund_schemes_from_rapidapi()
            if not fund_schemes:
                logger.info("No fund schemes fetched from RapidAPI")
                return
            current_time = datetime.datetime.now()
            scheme_mapping = await sql_handler.bulk_upsert_fund_schemes(
                [
                    {
                        "scheme_code": s["Scheme_Code"],
                        "scheme_name": s["Scheme_Name"],
                        "fund_family": s["Mutual_Fund_Family"],
                        "fund_type": s.get("Scheme_Type", "Unknown"),
                        "updated_at": current_time
                    }
                    for s in fund_schemes
                ]
            )
            nav_data = [
                {
                    "scheme_id": str(scheme_mapping[str(s["Scheme_Code"])]),
                    "nav": s["Net_Asset_Value"],
                    "updated_at": current_time
                }
                for s in fund_schemes if str(s["Scheme_Code"]) in scheme_mapping
            ]
            await sql_handler.bulk_upsert_nav_history(nav_data)

            logger.info(f"{len(fund_schemes)} schemes synced, investments updated")

        except Exception as e:
            logger.error(f"Error updating portfolios: {e}")

    @staticmethod
    async def fetch_fund_schemes_from_rapidapi():
        url = f"https://{RapidAPIConfig.RAPIDAPI_HOST}/latest?Scheme_Type=Open"
        headers = {
            "X-RapidAPI-Key": RapidAPIConfig.RAPIDAPI_KEY,
            "X-RapidAPI-Host": RapidAPIConfig.RAPIDAPI_HOST
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to fetch schemes: {response.text}")
                return []
            return response.json()
