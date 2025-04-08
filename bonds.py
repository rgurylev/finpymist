from typing import NamedTuple
import asyncio
from utils.datetime import *
from tinkoff.invest.schemas import RiskLevel
from tinkoff.invest import AsyncClient
from utils.finance import xirr
import os
import logging


logger = logging.getLogger(__name__)

TOKEN = os.environ["TINKOFF_TOKEN"]
risk = [RiskLevel.RISK_LEVEL_LOW]

class Bond(NamedTuple):
    name: str
    ticker: str
    days: int
    currency: str
    sector: str
    rate: float

def m2f(money):
    return round (money.units + money.nano / 10 ** 9, 2)

def get_days (bond):
    return (bond.maturity_date.replace(tzinfo=None) - TODAY).days

async def get_bond_xirr (bond = None, date =  MAX_DATE):
    async with AsyncClient(TOKEN) as client:
        result = None
        rate = None
        coupon_sum = 0
        #days = (bond.maturity_date.replace(tzinfo=None) - TODAY).days
        days = get_days(bond)
        if days > 360: return None
        try:
            price, coupons = await asyncio.gather(
                client.market_data.get_last_prices(figi=[bond.figi]),
                client.instruments.get_bond_coupons(figi=bond.figi, from_=datetime.today(), to=datetime(2050, 12, 31))
            )
            price = price.last_prices[0].price
            price = (price.units + price.nano / 10**9) * bond.nominal.units /100
            # формируем денежные потоки
            values = []
            operdates = []
            # добавляем в денежные потоки (цена на сегодня + НКД) со знаком "-"
            values.append( round ( (price +  m2f (bond.aci_value)),2)  * -1 )
            operdates.append (TODAY)
            # добавляем в денежные потоки купоны со знаком "+"
            for x in coupons.events:
                operdates.append (x.coupon_date.replace(tzinfo=None) )
                values.append(m2f (x.pay_one_bond) )
                coupon_sum += m2f (x.pay_one_bond)
            # добавляем номинал со знаком "+" в дату погашения
            values.append (bond.nominal.units)
            operdates.append (bond.maturity_date.replace(tzinfo=None))
            # добавляем налог на купон со знаком "-"
            values.append( round (coupon_sum * -0.13,2))
            operdates.append (bond.maturity_date.replace(tzinfo=None))
            # вычисляем чистую ставку
            rate = xirr(values, operdates, 365)

            logger.info(f'{bond.name:50}   {bond.ticker:15}      {days:4}  {bond.currency:3}   {bond.sector:20}   {rate:10}   {bond.figi}')
            result = Bond(**{'name': bond.name,
                             'ticker': bond.ticker,
                             'days': days,
                             'currency': bond.currency,
                             'sector': bond.sector,
                              'rate': rate
                            })
        except:
           print (f'Ошибка расчета доходности по облигации {bond.ticker}')
        return result

async def bonds():
    list = []
    try:
        async with AsyncClient(TOKEN) as client:
            bonds = await client.instruments.bonds()
            i = 0
            for bond in bonds.instruments:
                i+=1
                #days = (bond.maturity_date.replace(tzinfo=None) - TODAY).days
                days = get_days(bond)
                if bond.risk_level in risk and days < 360 and bond.currency == 'rub':
                    res = await get_bond_xirr (bond = bond)
                    if res.rate > 0.2: list.append(res)
                    # if i%30 == 0: await asyncio.sleep(1 / 1000)
        return list
    except Exception as e:
        logger.error(f"Failed {repr(e)}")
        return None


def paginate(list, page_size):
    for i in range(0, len(list), page_size):
        yield list[i:i + page_size]

async def bonds1():
    async with AsyncClient(TOKEN) as client:
        bonds = await client.instruments.bonds()
        list_bonds = [x for x in bonds.instruments if get_days(x) < 360 ]
        print(len (bonds.instruments))
        print(len(list_bonds))

        for page_number, page in enumerate(paginate(list_bonds, 100), start=1):
            print(f"Page {page_number}")
            res = await asyncio.gather(*(get_bond_xirr(x) for x in page))
            print(res)
            await asyncio.sleep(1/100)

        #res = await asyncio.gather(*(get_bond_xirr(x) for x in  list_bonds[0:100]))
        #time.sleep(2.0)
        #res = await asyncio.gather(*(get_bond_xirr(x) for x in list_bonds[100:300]))

        #i = 0
        #for bond in bonds.instruments:
        #    i+=1
        #    days = (bond.maturity_date.replace(tzinfo=None) - TODAY).days
        #    if bond.risk_level in risk and days < 360 and bond.currency == 'rub':
        #        rate = await get_bond_xirr (bond = bond)
        #        #if rate > 0.2:
        #        #    print(f'{bond.name:50}   {bond.ticker:15}      {days:4}  {bond.currency:3}   {bond.sector:20}   {rate:10}   {bond.figi}')
        #        if i%30 == 0: await asyncio.sleep(1 / 1000)
if __name__ == "__main__":
    asyncio.run(bonds())