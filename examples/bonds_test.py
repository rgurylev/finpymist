import os
import asyncio
import pandas as pd
import logging
import set_logger
from finpymist.bonds import bonds3


TOKEN = os.environ["TINKOFF_TOKEN"]
logger = logging.getLogger(__name__)

async def main():

    logger.info('begin....')
    list_bonds = await bonds3(max_days=9999, min_rate=0.13, limit=999)
    columns = ['name', 'ticker', 'figi', 'currency', 'days', 'price', 'rate', 'sector', 'risk', 'rank', 'coupons_last_date']
    list = [b.dict(columns) for b in list_bonds]
    df = pd.DataFrame(list)
    s = ''
    #for x in sorted (b, key=lambda x: -x['rate'] if x['rate'] else 0.0):
    #for x in b:
    #    s += f"{x['name']} \n" f"дней: {x['days']} ставка:{x['rate']*100:6.2f}\n\n"
    #print(s)
    #df = pd.DataFrame(sorted (b, key=lambda x: -x['rate']))

    #df = pd.DataFrame(b)
    df.to_excel("E:\\dev\\PycharmProjects\\finpymist\\bonds.xlsx")
    logger.info('end.')

if __name__ == "__main__":
    asyncio.run( main())
