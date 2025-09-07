import asyncio

import httpx
from sqlalchemy.orm import Session
from src.logging import logger

from src.config import RapidAPIConfig, SchedulerConfig
from src.db.pg.handler import SQLHandler
from src.db.pg.sessions import get_db


class SchedulerHandler:

    # Background task for portfolio updates
    async def update_portfolios_task(self, ):
        if SchedulerConfig.SCHEDULER_ENABLED:
            while True:
                try:
                    await self.update_all_portfolios()
                    await asyncio.sleep(delay=SchedulerConfig.SCHEDULER_INTERVAL_SECONDS)
                except Exception as e:
                    logger(f"Error updating portfolios: {e}")
                    await asyncio.sleep(SchedulerConfig.SCHEDULER_INTERVAL_SECONDS)
        else:
            logger("Scheduler Disabled. Please enable and restart module")

    async def update_all_portfolios(self):
        db: Session = next(get_db())
        sql_handler = SQLHandler(session=db)
        fund_schemes = await self.fetch_fund_schemes_from_rapidapi()
        if not fund_schemes:
            logger.info("No fund schemes fetched from RapidAPI")
        for scheme in fund_schemes:
            fund_scheme = await sql_handler.upsert_fund_schemes(fund_schemes={
                "scheme_code": scheme["Scheme_Code"],
                "scheme_name": scheme["Scheme_Name"],
                "fund_family": scheme["Mutual_Fund_Family"],
                "fund_type": scheme.get("Scheme_Type", "Unknown"),
            })
            await sql_handler.upsert_nav_history({
                "scheme_id": fund_scheme,
                "nav": scheme['Net_Asset_Value']
            })

        logger(f"{len(fund_schemes)} schemes synced, investments updated")

    @staticmethod
    async def fetch_fund_schemes_from_rapidapi():
        url = f"https://{RapidAPIConfig.RAPIDAPI_HOST}/latest?Scheme_Type=Open"
        headers = {
            "X-RapidAPI-Key": RapidAPIConfig.RAPIDAPI_KEY,
            "X-RapidAPI-Host": RapidAPIConfig.RAPIDAPI_HOST
        }
        response = httpx.get(url, headers=headers, timeout=60)
        if response.status_code != 200:
            logger(f"Failed to fetch schemes:{response.text}")
            return []
        return response.json()
