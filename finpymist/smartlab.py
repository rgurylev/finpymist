from bs4 import BeautifulSoup
import json
import logging
from finpymist.utils.html import HtmlLoader
from typing import Final
from settings import DATA_DIR
import set_logger

logger = logging.getLogger(__name__)

RANKS_FILE : Final[str] = DATA_DIR / 'ranks.json'

async def get_ranks(ids):

    try:
        with open(RANKS_FILE, 'r') as file:
            ranks = json.load(file)
    except Exception as e:
        logger.info(f'ошибка открытия файла ranks.json')
        ranks ={}

    loader = HtmlLoader()
    urls = [ (id, f'https://smart-lab.ru/q/bonds/{id}') for id in ids if ranks.get(id) == None]
    logger.warning ('начали загрузку рейтингов с smart-lab.ru...')
    async for id, url, html in loader.load2(urls):
        ranks[id] = get_rank(html)
    with open(RANKS_FILE, "w", encoding="utf-8") as file:
        json.dump(ranks, file)
    return ranks

def get_rank(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        label = soup.find('div', string='Кредитный рейтинг')
        if label:
            value_container = label.find_next_sibling('div')
            rating_text = value_container.select_one('.linear-progress-bar__text')
            if rating_text:
                rank = rating_text.get_text(strip=True)
                return rank
        return None
    except Exception as e:
        logger.error(f'Ошибка определения кредитного рейтинга облигации: {e}')
        return None