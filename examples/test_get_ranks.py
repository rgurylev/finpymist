import asyncio
#from finpymist.moex import get_ranks
from finpymist.smartlab import get_ranks

# пример загрузки кредитных рейтингов облигаций с сайтов smart-lab.ru и moex.com

async def main():
    ids = ['RU000A106K43', 'RU000A107AJ0', 'RU000A10CKS5', 'RU000A106YH6', 'RU000A1014J2',
           'RU000A10BGF2', 'RU000A0JXQ44', 'RU000A0ZYJ91', 'RU000A109B33', 'RU000A10CQ85']

    #urls = ['https://www.moex.com/ru/issue.aspx?board=TQCB&code=RU000A101Z74#/bond_1',
    #        'https://www.moex.com/ru/issue.aspx?board=TQCB&code=RU000A10CC99#/bond_1',
    #        'https://www.moex.com/ru/issue.aspx?board=TQCB&code=RU000A10CKS5#/bond_1']
    #urls = [f'https://www.moex.com/ru/issue.aspx?board=TQCB&code={id}#/bond_1' for id in ids]

    # urls = [(id, f'https://smart-lab.ru/q/bonds/{id}') for id in ids]

    ranks = await get_ranks(ids)
    ranks = [(k, v) for k, v in ranks.items() ]
    print (ranks)
    #page = await get_html2('https://smart-lab.ru/q/bonds/RU000A105PH6')
    #loader = HtmlLoader()
    #async for i, _, html in loader.load2(urls, 10):
    #    print (f'{i} {html[:20]}')

    #print (page)


#pages = await loader.load(urls)
    #sleep(10)
    #i=1
    #for x in pages:
        #print (x[:1000])
        #with open(f"{i}.html", "w") as file:
        #    file.write(x)
        #i+=1
        #get_rate2(x)
        #rank = get_rank2(x)
        #print(rank)



if __name__ == "__main__":
    asyncio.run( main())

