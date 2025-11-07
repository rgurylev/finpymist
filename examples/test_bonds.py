import asyncio
import pandas as pd
import logging
import set_logger
from finpymist.bonds import bonds


logger = logging.getLogger(__name__)

async def main():

    logger.info('begin....')
    list_bonds = await bonds(max_days=9999, min_rate=0.13, limit=10)
    columns = ['name', 'ticker', 'figi', 'currency', 'days', 'price', 'rate', 'sector', 'risk', 'rank', 'coupons_last_date']
    list = [b.dict(columns) for b in list_bonds]
    df = pd.DataFrame(list)
    df.to_excel("E:\\dev\\PycharmProjects\\finpymist\\bonds.xlsx")
    logger.info('end.')

if __name__ == "__main__":
    asyncio.run( main())
