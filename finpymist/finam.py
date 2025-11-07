from typing import Optional
from urllib.parse import urljoin
from pathlib import Path
import logging
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from finpymist.utils.html import get_html

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).strip().lower()

def _extract_issue_link_from_first_row(html: str, base_url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    # Find any table that has a header cell with text "Выпуск"
    for table in soup.find_all("table"):
        # Try to find a header row
        header_row = None
        for candidate_row in table.find_all("tr"):
            cells = candidate_row.find_all(["th", "td"])
            if not cells:
                continue
            texts = [_normalize_text(c.get_text(" ", strip=True)) for c in cells]
            if "выпуск" in texts:
                header_row = candidate_row
                issue_col_index = texts.index("выпуск")
                break
        if header_row is None:
            continue

        # Prefer rows in tbody after header row
        data_row = None
        # If the header is in thead, go to tbody
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                tds = tr.find_all("td")
                if tds:
                    data_row = tr
                    break
        # Fallback: next tr siblings after header
        if data_row is None:
            for tr in header_row.find_next_siblings("tr"):
                tds = tr.find_all("td")
                if tds:
                    data_row = tr
                    break
        if data_row is None:
            continue

        cells = data_row.find_all("td")
        if issue_col_index >= len(cells):
            continue
        cell = cells[issue_col_index]
        link_tag = cell.find("a", href=True)
        if not link_tag:
            # If no <a>, try the whole cell text as URL (unlikely)
            candidate = cell.get_text(" ", strip=True)
            return urljoin(base_url, candidate) if candidate else None
        return urljoin(base_url, link_tag.get("href"))
    return None

async def get_oferta(isin):
    try:
        url = f'https://bonds.finam.ru/issue/search/default.asp?operatorIdName=&operatorTypeName=&quoteType=1&Code=&srchString={isin}'
        html = await get_html(url)
        Path(__file__).with_name("content.html").write_text(html, encoding="utf-8")
        issue_link = _extract_issue_link_from_first_row(html, base_url=url)
        if not issue_link:
            print("Не удалось найти ссылку на выпуск в первой строке.")
            return None
        return issue_link
    except Exception as e:
        logger.error(f'Ошибка определения даты оферты {isin}: {e}')
        return




