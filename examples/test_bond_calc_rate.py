import os
import logging
import asyncio
from finpymist.bonds import BondsService
import set_logger

logger = logging.getLogger(__name__)

TOKEN = os.environ["TINKOFF_TOKEN"]

async def main():
    ticker =  'RU000A105PH6'
    with BondsService() as service:
        bond = await service.bond_ext(ticker)
        service.details_to_excel(bond, f'{ticker}_details.xlsx')
        print (f'rate:{bond.rate}  rank:{bond.rank}')

if __name__ == "__main__":
    asyncio.run(main())