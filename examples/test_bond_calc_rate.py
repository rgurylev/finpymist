import os
import logging
import asyncio
from finpymist.bonds import Bond, bond_ext, details_to_excel
import set_logger

logger = logging.getLogger(__name__)

TOKEN = os.environ["TINKOFF_TOKEN"]

async def main():
    ticker =  'RU000A105PH6'
    bond = await bond_ext(ticker)
    details_to_excel(bond, f'{ticker}_details.xlsx')

if __name__ == "__main__":
    asyncio.run(main())