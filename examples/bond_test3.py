import asyncio
from tinkoff.invest import AsyncClient
from tinkoff.invest.schemas import InstrumentIdType
from settings import TINKOFF_TOKEN
from playwright.async_api import async_playwright
from finpymist import moex
from finpymist.bonds import Bond
from finpymist.utils.html import get_html


from finpymist.currency import get_rate_async

import logging
import set_logger
log = logging.getLogger(__name__)

async def from_moex(isin):
    url = 'https://smart-lab.ru/q/bonds/' + isin
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                                             "Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        with open(isin + '.html', "w") as f:
            f.write(html)
    # print(html)
        await browser.close()


async def get_bond_2 (id):
    async with AsyncClient(TINKOFF_TOKEN) as client:
        b = await client.instruments.bond_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code='TQCB',
                                          id=id)
        return b.instrument


async def main():
    b = await get_bond_2('RU000A103DT2')
    bond = Bond.create(b)
    #bond = await get_bond_2('RU000A107JN3')
    '''
    bond_ext = Bond(name=bond.name,
                  ticker=bond.ticker,
                  figi=bond.figi,
                  currency=bond.currency,
                  nominal=bond.nominal,
                  aci_value=bond.aci_value,
                  maturity_date=bond.maturity_date.replace(tzinfo=None),
                  sector=bond.sector,
                  risk=bond.risk_level
                  )
     '''
    #await bond_ext.get_price()
    await bond.calc_rate()
    await bond.get_rank()
    log.info(bond)
    log.info(f'rate: {bond.rate}')
    #log.info(f'rank: {bond_ext.rank}')
    print (bond.dict(['name', 'ticker', 'rank']))
    #print(security['COUPONPERCENT'])
    #print (f'rate: {rate}')

if __name__ == "__main__":
    asyncio.run(main())
