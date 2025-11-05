import os
import logging
import asyncio
from bs4 import BeautifulSoup
from tinkoff.invest import AsyncClient, Client
from tinkoff.invest.schemas import MoneyValue
from tinkoff.invest.schemas import RiskLevel
from tinkoff.invest.schemas import InstrumentIdType
from finpymist.utils.datetime import *
from finpymist.utils.finance import xirr
from finpymist.currency import get_rate_async
from finpymist.smartlab import get_ranks
from finpymist.utils.concurency import execute_method, execute_func
from finpymist.moex import get_oferta
from tinkoff_.async_smart_client import AsyncSmartClient

MAX_DAYS = 1000
MIN_RATE = 0.2
TAX = 0.13
INF_INT = 10**10
RISK = [RiskLevel.RISK_LEVEL_LOW, RiskLevel.RISK_LEVEL_MODERATE]
TODAY = date.today()

#import set_logger
logger = logging.getLogger(__name__)
TOKEN = os.environ["TINKOFF_TOKEN"]

class Bond:
    def __init__(self, name: str, ticker: str, figi: str, currency: str,
                 nominal: MoneyValue, aci_value: MoneyValue,
                 maturity_date, sector: str, risk: int):
        self.name = name
        self.ticker = ticker
        self.figi = figi
        self.currency = currency
        self.nominal = nominal
        self.aci_value = aci_value
        self.maturity_date = maturity_date
        self.sector = sector
        self.risk = risk
        self.days = (self.maturity_date - TODAY).days
        self.rate = None
        self.price = None
        self.coupons = None
        self.currate = None
        self.rank = None
        self.oferta_date = None
        self.call_date = None
        self.put_date = None
        self.coupons_last_date = None
        self.cash_flow = None

    @classmethod
    def create (cls, bond):
        return cls     (name=bond.name,
                        ticker=bond.ticker,
                        figi=bond.figi,
                        currency=bond.currency,
                        nominal=bond.nominal,
                        aci_value=bond.aci_value,
                       # maturity_date=bond.maturity_date.replace(tzinfo=None),
                        maturity_date=bond.maturity_date.date(),
                        sector=bond.sector,
                        risk=bond.risk_level
                        )
    def create_by_ticker (ticker):
        with Client(TOKEN) as client:
            try:
                    bond = client.instruments.bond_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                                      class_code='TQCB', id=ticker).instrument
                    print (bond)
                    return Bond.create(bond)
            except Exception as e:
                logger.error(f'Ошибка создания облигации {ticker}: {e} ')

    def __str__(self):
        return (f"Investment(name={self.name}, ticker={self.ticker}, currency={self.currency}, nominal.currency={self.nominal.currency}, "
                f"nominal.units={self.nominal.units}, sector={self.sector}, days={self.days}, risk={self.risk}, rank={self.rank} price={self.price}, rate={self.rate} "
                f"coupons_last_date={self.coupons_last_date}"
                )

    def dict (self, items):
        result = {item: getattr(self, item, None) for item in items}
        return result

    """
    async def get_price(self):
        async with AsyncClient(TOKEN) as client:
            try:
                price, self.currate = await asyncio.gather(
                    client.market_data.get_last_prices(figi=[self.figi]),
                    get_rate_async(self.nominal.currency)
                )
                price = price.last_prices[0].price
                self.price = (price.units + price.nano / 10 ** 9) * self.nominal.units / 100
            except Exception as e:
                logger.error(f'Ошибка определения цены облигации {self.ticker}: {e} ')

    async def get_coupons(self):
        async with AsyncClient(TOKEN) as client:
            try:

                  self.coupons = await client.instruments.get_bond_coupons(figi=self.figi, from_=datetime.today(),
                                                        to=datetime(2050, 12, 31))
                  #self.coupons = coupons
            except Exception as e:
                logger.error(f'Ошибка получения графика выплаты купонов по облигации {self.ticker}: {e} ')
    async def get_rank(self):
        url = 'https://smart-lab.ru/q/bonds/' + self.ticker
        print(f'url: {url}')
        try:
            html = await get_html(url)
            soup = BeautifulSoup(html, 'html.parser')

        # Find the element containing the label
            label = soup.find('div', string='Кредитный рейтинг')

        # Find the next sibling that contains the value
            if label:
                value_container = label.find_next_sibling('div')
                rating_text = value_container.select_one('.linear-progress-bar__text')
                if rating_text:
                    self.rank = rating_text.get_text(strip=True)
        except Exception as e:
           logger.error (f'Ошибка определения кредитного рейтинга облигации {self.ticker}: {e}')
    """

    async def calc_rate(self):
        end_date = min (self.maturity_date, self.oferta_date if self.oferta_date else self.maturity_date)
        coupons_last_date = None
        # if self.price == None:
        #     await self.get_price()
        # if self.coupons == None:
        #     await self.get_coupons()
        if self.price:
            coupon_sum = 0
            # формируем денежные потоки
            values = []
            operdates = []
            # добавляем в денежные потоки (цена на сегодня + НКД) со знаком "-"
            values.append(round((self.price*self.currate + m2f(self.aci_value)), 2) * -1)
            operdates.append(TODAY)
            # добавляем в денежные потоки купоны со знаком "+"
            if self.coupons:
                for x in self.coupons:
                    #operdates.append(x.coupon_date.replace(tzinfo=None))
                    if not (x.pay_one_bond.units == 0):
                        operdates.append(x.coupon_date.date())
                        coupon_value = m2f(x.pay_one_bond) * self.currate
                        values.append(coupon_value)
                        coupon_sum += coupon_value
                        self.coupons_last_date = x.coupon_date.date()
                    else:
                        # self.coupons_last_date = coupons_last_date
                        break
            # добавляем номинал со знаком "+" в дату погашения
            values.append(self.nominal.units * self.currate)
            operdates.append(self.coupons_last_date if self.coupons_last_date else end_date)
            # добавляем налог на купон со знаком "-"
            values.append(round(coupon_sum * -TAX, 2))
            operdates.append(end_date)
            # вычисляем чистую ставку
            self.rate = xirr(values, operdates, 365)
            #await asyncio.sleep(1 )
            self.cash_flow = (operdates, values)
            #for d, v in zip(operdates, values):
            #    logger.debug (f'{d}      {v}')


# функции  получения атрибутов облигации

async def get_price(bond):
        async with AsyncClient(TOKEN) as client:
            try:
                #price, self.currate = await asyncio.gather(
                #    client.market_data.get_last_prices(figi=[self.figi]),
                #    get_rate_async(self.nominal.currency)
                #)
                #price = price.last_prices[0].price
                #self.price = (price.units + price.nano / 10 ** 9) * self.nominal.units / 100
                price = await client.market_data.get_last_prices(figi=[bond.figi])
                price = price.last_prices[0].price
                price = (price.units + price.nano / 10 ** 9) * bond.nominal.units / 100
                return price
            except Exception as e:
                logger.error(f'Ошибка определения цены облигации {bond.ticker}: {e} ')
                return None

async def get_coupons(bond):
                async with AsyncClient(TOKEN) as client:
                    try:

                        coupons = await client.instruments.get_bond_coupons(figi=bond.figi, from_=datetime.today(),
                                                                                 to=datetime(2050, 12, 31))
                        return coupons.events
                        # self.coupons = coupons
                    except Exception as e:
                        logger.error(f'Ошибка получения графика выплаты купонов по облигации {bond.ticker}: {e} ')
                        return None


async def get_rank(isin):
        url = 'https://smart-lab.ru/q/bonds/' + isin
        logger.debug(f'get_rank: {url}')
        try:
            html = await get_html(url)
            soup = BeautifulSoup(html, 'html.parser')

        # Find the element containing the label
            label = soup.find('div', string='Кредитный рейтинг')

        # Find the next sibling that contains the value
            if label:
                value_container = label.find_next_sibling('div')
                rating_text = value_container.select_one('.linear-progress-bar__text')
                if rating_text:
                    rank = rating_text.get_text(strip=True)
                    return (isin, rank)
            return (isin, None)
        except Exception as e:
           logger.error (f'Ошибка определения кредитного рейтинга облигации {isin}: {e}')
           return (isin, None)

#

def m2f(money):
    return round (money.units + money.nano / 10 ** 9, 2)

def paginate_list(items, page_size, page_number):
    """Returns a slice of the list for the given page number and page size."""
    start = (page_number - 1) * page_size
    end = start + page_size
    return items[start:end]

async def bonds(max_days = 99999, min_rate = -1.0, limit = None):
    bonds = []
#    columns = ['name', 'ticker', 'figi', 'currency', 'days', 'price', 'rate', 'sector', 'risk', 'rank']
    i = 0
    #try:
    async with AsyncClient(TOKEN) as client:
        bonds_response = await client.instruments.bonds()
    for b in bonds_response.instruments:
            i+=1
            #if not (b.isin=='RU000A10B1N3'): continue
            if limit and i > limit: break
            if 'ОФЗ' in b.name.upper(): continue
            bond = Bond.create(b)
            bond.price, coupons, bond.currate = await asyncio.gather(
                get_price(bond),
                get_coupons(bond),
               # get_oferta(bond.ticker),
                get_rate_async(bond.nominal.currency)
            )
            bond.coupons = sorted(coupons, key=lambda x: x.coupon_number)
            #if bond.coupons[len(bond.coupons) - 1].pay_one_bond.units == 0:
            #    logger.debug(f'Последний купон {bond.ticker} = 0. Ищем дату оферты')
            #    bond.oferta_date, bond.call_date, bond.put_date = await get_oferta(bond.ticker)

            if bond.risk in RISK and bond.days<=max_days and bond.currency=='rub' and bond.nominal.currency=='rub':
                await bond.calc_rate()
                if bond.rate == None or bond.rate >= min_rate:
                    bonds.append(bond)
                    logger.info (bond)
                #if bond.rate == None or bond.rate>= min_rate:
                    #await bond.get_rank()
                    #list.append(bond.dict(columns))
                #    i += 1
                    #if i > 10: break
                # if i%30 == 0: await asyncio.sleep(1 / 1000)
            #print(i)

    # добавляем кредитный рейтинг
    ranks = await execute_func([x.ticker for x in bonds], page_size=10, delay=1, func_name=get_rank)
    #print (ranks)
    for  b, r in zip (sorted (bonds, key = lambda x: x.ticker) , sorted (ranks, key = lambda x: x[0])):
       b.rank = r[1]
       #print (b)
    #await execute_method(bonds, page_size=5, method_name='calc_rate')
    #bonds = [b for b in bonds if b.rate == None or b.rate>= min_rate]
    #await execute_method(bonds, page_size=10, method_name='get_rank')

    #page_size = 10
    #total_pages = (len(bonds) + page_size - 1) // page_size
    #№for page_number in range(1, total_pages + 1):
    #    z = paginate_list(bonds, page_size, page_number)
    #    await asyncio.gather(*[b.get_rank() for b in z])

    #await asyncio.gather(*[b.get_rank() for b in bonds if b.rate == None or b.rate>= min_rate])
    #list = [b.dict(columns) for b in bonds if bond.rate == None or bond.rate>= min_rate]
    #list = [b.dict(columns) for b in bonds]
    return bonds
    #except Exception as e:
    #   logger.error(f"Failed {repr(e)}")
    #   return None

async def bonds2(max_days = 99999, min_rate = -1.0):
    list = []
    columns = ['name', 'ticker', 'figi', 'currency', 'days', 'price', 'rate', 'sector', 'risk', 'rank']
    try:
       async with AsyncClient(TOKEN) as client:
            bonds = await client.instruments.bonds()
       i = 0
       k = 0
       n = len(bonds.instruments)
       for b in bonds.instruments:
                bond = Bond.create(b)
                #days = (bond.maturity_date.replace(tzinfo=None) - TODAY).days
                k += 1
                if bond.risk in RISK and bond.days<=max_days and bond.currency=='rub' and bond.nominal.currency=='usd':
                    await bond.calc_rate ()
                    logger.info (b)
                    if bond.rate == None or bond.rate>= min_rate:
                        await bond.get_rank()
                        list.append(bond.dict(columns))
                        i += 1
                        #if i > 10: break
                    # if i%30 == 0: await asyncio.sleep(1 / 1000)
                #print(i)
       return list
    except Exception as e:
        logger.error(f"Failed {repr(e)}")
        return None

async def bonds3(max_days = 99999, min_rate = -1.0, limit = None):
    bonds = []
#    columns = ['name', 'ticker', 'figi', 'currency', 'days', 'price', 'rate', 'sector', 'risk', 'rank']
    i = 0
    #try:
    client = AsyncSmartClient(TOKEN)
    try:
        await client.connect()
        bonds_response = await client.bonds()
        for b in bonds_response:
                #if b.figi not in ['RU000A101Z74']: continue
                i+=1
                #if not (b.isin=='RU000A10B1N3'): continue
                if limit and i > limit: break
                if 'ОФЗ' in b.name.upper(): continue
                bond = Bond.create(b)
                prices, coupons, bond.currate = await asyncio.gather(
                    client.get_last_prices([bond.figi]),
                    client.get_bond_coupons(bond.figi),
                   # get_oferta(bond.ticker),
                    get_rate_async(bond.nominal.currency)
                )
                #bond.coupons = [x for x in coupons if x.coupon_date.date() > TODAY]
                bond.coupons = sorted(coupons, key=lambda x: x.coupon_number)
                bond.price = (prices[0].price.units + prices[0].price.nano / 10 ** 9) * bond.nominal.units / 100
                #if bond.coupons[len(bond.coupons) - 1].pay_one_bond.units == 0:
                #    logger.debug(f'Последний купон {bond.ticker} = 0. Ищем дату оферты')
                #    bond.oferta_date, bond.call_date, bond.put_date = await get_oferta(bond.ticker)

                if bond.risk in RISK and bond.days<=max_days and bond.currency=='rub' and bond.nominal.currency=='rub':
                    await bond.calc_rate()
                    if bond.rate == None or bond.rate >= min_rate:
                        bonds.append(bond)
                        logger.info (bond)
                    #if bond.rate == None or bond.rate>= min_rate:
                        #await bond.get_rank()
                        #list.append(bond.dict(columns))
                    #    i += 1
                        #if i > 10: break
                    # if i%30 == 0: await asyncio.sleep(1 / 1000)
                #print(i)

        # добавляем кредитный рейтинг
        ranks = await get_ranks([x.ticker for x in bonds])
        for  b, r in zip (sorted (bonds, key = lambda x: x.ticker) , sorted (ranks, key = lambda x: x[0])):
           b.rank = r[1]

        #await execute_method(bonds, page_size=5, method_name='calc_rate')
        #bonds = [b for b in bonds if b.rate == None or b.rate>= min_rate]
        #await execute_method(bonds, page_size=10, method_name='get_rank')

        #page_size = 10
        #total_pages = (len(bonds) + page_size - 1) // page_size
        #№for page_number in range(1, total_pages + 1):
        #    z = paginate_list(bonds, page_size, page_number)
        #    await asyncio.gather(*[b.get_rank() for b in z])

        #await asyncio.gather(*[b.get_rank() for b in bonds if b.rate == None or b.rate>= min_rate])
        #list = [b.dict(columns) for b in bonds if bond.rate == None or bond.rate>= min_rate]
        #list = [b.dict(columns) for b in bonds]
        return bonds
    #except Exception as e:
    #   logger.error(f"Failed {repr(e)}")
    #   return None
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(bonds())