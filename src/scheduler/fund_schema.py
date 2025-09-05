import asyncio

import httpx
from sqlalchemy.orm import Session

from src.config import RapidAPIConfig, SchedulerConfig
from src.db.pg.handler import SQLHandler
from src.db.pg.sessions import get_db
from src.exceptions import MutualFundException


class SchedulerHandler:

    # Background task for portfolio updates
    async def update_portfolios_task(self, ):
        if SchedulerConfig.SCHEDULER_ENABLED:
            while True:
                try:
                    await self.update_all_portfolios()
                    await asyncio.sleep(delay=SchedulerConfig.SCHEDULER_INTERVAL_SECONDS)
                except Exception as e:
                    print(f"Error updating portfolios: {e}")
                    await asyncio.sleep(SchedulerConfig.SCHEDULER_INTERVAL_SECONDS)
        else:
            print("Scheduler Disabled. Please enable and restart module")

    async def update_all_portfolios(self):
        db: Session = next(get_db())
        sql_handler = SQLHandler(session=db)
        fund_schemes = await self.fetch_fund_schemes_from_rapidapi()
        if not fund_schemes:
            raise MutualFundException(message="Failed to fetch the rapidapi data")
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

        print(f"{len(fund_schemes)} schemes synced, investments updated")

    @staticmethod
    async def fetch_fund_schemes_from_rapidapi():
        url = f"https://{RapidAPIConfig.RAPIDAPI_HOST}/latest?Scheme_Type=Open"
        headers = {
            "X-RapidAPI-Key": RapidAPIConfig.RAPIDAPI_KEY,
            "X-RapidAPI-Host": RapidAPIConfig.RAPIDAPI_HOST
        }
        response = httpx.get(url, headers=headers, timeout=60)
        if response.status_code != 200:
            print("Failed to fetch schemes:", response.text)
            return [{
  "Date": "04-Sep-2025",
  "ISIN_Div_Payout_ISIN_Growth": "INF209KA12Z1",
  "ISIN_Div_Reinvestment": "INF209KA13Z9",
  "Mutual_Fund_Family": "Aditya Birla Sun Life Mutual Fund",
  "Net_Asset_Value": 100.1379,
  "Scheme_Category": "Debt Scheme - Banking and PSU Fund",
  "Scheme_Code": 119551,
  "Scheme_Name": "Aditya Birla Sun Life",
  "Scheme_Type": "Open Ended "
}]
        return response.json()
