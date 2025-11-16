import asyncio
from finpymist.bonds import BondsService
import set_logger

# пример загрузки кредитных рейтингов облигаций с сайтов smart-lab.ru и moex.com

async def main():
    ids = ['RU000A106K43', 'RU000A107AJ0', 'RU000A10CKS5', 'RU000A106YH6', 'RU000A1014J2',
           'RU000A10BGF2', 'RU000A0JXQ44', 'RU000A0ZYJ91', 'RU000A109B33', 'RU000A10CQ85']

    #urls = ['https://www.moex.com/ru/issue.aspx?board=TQCB&code=RU000A101Z74#/bond_1',
    #        'https://www.moex.com/ru/issue.aspx?board=TQCB&code=RU000A10CC99#/bond_1',
    #        'https://www.moex.com/ru/issue.aspx?board=TQCB&code=RU000A10CKS5#/bond_1']
    #urls = [f'https://www.moex.com/ru/issue.aspx?board=TQCB&code={id}#/bond_1' for id in ids]

    # urls = [(id, f'https://smart-lab.ru/q/bonds/{id}') for id in ids]

    try:
        with BondsService() as service:
            ranks = await service.get_ranks(ids)
            print (ranks)
    except ValueError as e:
        print(f"Поймано исключение: {e}")


if __name__ == "__main__":
    asyncio.run( main())