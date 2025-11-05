import aiohttp
from typing import Final
import logging
import json
from bs4 import BeautifulSoup
from datetime import datetime
from finpymist.utils.html import HtmlLoader
from finpymist.utils.html import HtmlLoader
from settings import DATA_DIR
import set_logger

logger = logging.getLogger(__name__)

RANKS_FILE : Final[str] = DATA_DIR / 'ranks.json'


# облигации
async def get_oferta(isin):
    url = f'https://www.moex.com/ru/issue.aspx?board=TQCB&code={isin}#/bond_1'
    print(f'url: {url}')
    def get_value(div, name):
        th = div.find ('th', string = name)
        if th:
            value = th.find_next_sibling('td').text.strip()
            value = convert_value (value, 'date')
        return value

    try:
        #html = await get_html2(url)
        html = None
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', id='bond_1')
        oferta_date = get_value(div, 'Дата Оферты')
        put_date = get_value(div, 'Дата пут-опциона')
        call_date = get_value(div, 'Дата колл-опциона')
        return oferta_date, call_date, put_date
    except Exception as e:
        logger.error(f'Ошибка определения даты оферты {isin}: {e}')


def get_rank (html):
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='emitent-credit-rating-table table-fixed-layout')
        #try:
        if table:
            # Находим первую строку в tbody
            first_row = table.find('tbody').find('tr')

            # Получаем все ячейки первой строки
            cells = first_row.find_all('td')
            if len(cells) >= 2:
                credit_rating = cells[1].get_text(strip=True)
                print(f"Значение кредитного рейтинга: {credit_rating}")
                return  credit_rating
            else:
                print("Недостаточно столбцов в строке")
        else:
            print("Таблица не найдена")
    return None

async def get_ranks(ids):
    try:
        with open(RANKS_FILE, 'r') as file:
            ranks = json.load(file)
    except Exception as e:
        logger.info(f'ошибка открытия файла ranks.json')
        ranks ={}

    urls = [(id, f'https://www.moex.com/ru/issue.aspx?board=TQCB&code={id}#/bond_1') for id in ids  if ranks.get(id) == None]
    loader = HtmlLoader()
    selector = 'table.emitent-credit-rating-table.table-fixed-layout'
    logger.info('начали загрузку рейтингов с moex.com...')
    async for id, url, html in loader.load2(urls, page_size=5, selector=selector):
        ranks[id] = get_rank(html)
        #print(f'Кредитный рейтинг: {id}: {rank}')
    with open(RANKS_FILE, "w", encoding="utf-8") as file:
        json.dump(ranks, file)
    return ranks

def convert_value(value: str, target_type: str):
    match target_type.lower():
        case "string":
            return value

        case "date":
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            #raise ValueError(f"Cannot convert '{value}' to date. Unsupported format.")
            return None

        case "number":
            try:
                return float(value) if '.' in value else int(value)
            except ValueError:
                #raise ValueError(f"Cannot convert '{value}' to number.")
                return None

        case "boolean":
            val = value.lower()
            if val in ("true", "1", "yes"):
                return True
            elif val in ("false", "0", "no"):
                return False
            else:
                #raise ValueError(f"Cannot convert '{value}' to boolean.")
                return None
        case _:
            raise ValueError(f"Unsupported target type: {target_type}")


async def get_security (name):
    # https://iss.moex.com/iss/securities/RU000A107JN3.json
    url = f"https://iss.moex.com/iss/securities/{name}.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()  # Raises an exception for non-200 responses
            data = await response.json()
            security = {s[0]: convert_value(s[2], s[3]) for s in data['description']["data"]}
            return security



"""

async def fetch(isin):
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
"""


