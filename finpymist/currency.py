import aiohttp
import asyncio
from functools import lru_cache
import xml.etree.ElementTree as ET
from datetime import datetime
from async_lru import alru_cache

import logging
import set_logger
log = logging.getLogger(__name__)



def get_rate(code, date = datetime.now()) -> float:
    """Synchronous wrapper for caching based on date."""
    return asyncio.run(get_rate_async(code, date))

@alru_cache(maxsize=128)
async def get_rate_async(code, date = datetime.now()):
    if code.upper() == 'RUB':
        return 1
    datestr = date.strftime("%d/%m/%Y")
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={datestr}"
    log.info(f'url: {url}')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml_text = await response.text()

    root = ET.fromstring(xml_text)

    for valute in root.findall('Valute'):
        char_code = valute.find('CharCode')
        if char_code is not None and char_code.text == code.upper():
            value = valute.find('Value')
            if value is not None:
                # Convert value from '##,##' to float
                return float(value.text.replace(',', '.'))

    return None


rate = asyncio.run(get_rate_async("usd"))
rate = asyncio.run(get_rate_async("usd"))

