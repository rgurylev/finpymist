import logging
import asyncio
from finpymist.utils.concurency import execute_tasks
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

BROWSER_ARGS = [
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-sync",
    "--metrics-recording-only",
    "--mute-audio",
    "--no-first-run",
    "--safebrowsing-disable-auto-update",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-features=TranslateUI,site-per-process"
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
              "AppleWebKit/537.36 (KHTML, like Gecko) " \
              "Chrome/122.0.0.0 Safari/537.36"

class HtmlLoader:
    def __init__(self):
        self.browser_ = None
        self.context_ = None
        self.semaphore = asyncio.Semaphore(5)
    '''
    async def get_html(self, url):
        # Block images, fonts, and media
        async def block_resources(route, request):
            if request.resource_type in ["image", "media", "font"]:
                await route.abort()
            else:
                await route.continue_()

        logger.debug('url')
        print (f'url: {url[1]}')
        #async with self.semaphore:
        page = await self.context_.new_page()
        await page.route("**/*", block_resources)
        await page.goto(url[1], wait_until="load")
        print (f'url: {url[1]} goto')
        html = await page.content()
        print (f'url: {url[1]} page.content')
        await page.close()
        return url[0], url[1], html
    '''
    async def get_html(self, url, selector):
        async def block_resources(route, request):
            if request.resource_type in ["image", "media", "font"]:
                await route.abort()
            else:
                await route.continue_()
        html = None
        print (url)
        #async with self.semaphore:
        async with async_playwright() as p:

           try:
                browser = await p.chromium.launch(headless=True,
                                                  args=BROWSER_ARGS
                                                  )
                context = await browser.new_context(user_agent=USER_AGENT)
                page = await context.new_page()
                await page.route("**/*", block_resources)
                #await page.goto(url[1], wait_until="load")
                await page.goto(url[1])
                if selector:
                   await page.wait_for_selector('table.emitent-credit-rating-table.table-fixed-layout', timeout=15000)
                html = await page.content()
                await page.close()
           except Exception as e:
                logger.error(f"Ошибка при загрузке страницы {url}: {e}")
           finally:
                await context.close()
                await browser.close()
        return url[0], url[1], html

    '''
    async def load(self, urls):
            #async with async_playwright() as playwright:
            #self.browser_ = await playwright.chromium.launch(headless=True,
            #                                  args=BROWSER_ARGS)
            #self.context_ = await self.browser_.new_context(user_agent=USER_AGENT)
            tasks = [ self.get_html(url) for url in urls ]
            #pages = await asyncio.gather(*tasks)
            for future in asyncio.as_completed(tasks):
                result = await future
                yield result
            #await self.context_.close()
            #await self.browser_.close()
    '''
    async def load2(self, urls, page_size = 10, selector = None):
            tasks = [ self.get_html(url, selector) for url in urls ]
            async for x in execute_tasks (tasks, page_size = page_size):
                yield x
            #for future in asyncio.as_completed(tasks):
            #    result = await future
            #    yield result
'''
async def get_html2(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,
                                          args=[
                                              "--disable-gpu",
                                              "--disable-dev-shm-usage",
                                              "--no-sandbox",
                                              "--disable-setuid-sandbox",
                                              "--disable-extensions",
                                              "--disable-background-networking",
                                              "--disable-default-apps",
                                              "--disable-sync",
                                              "--metrics-recording-only",
                                              "--mute-audio",
                                              "--no-first-run",
                                              "--safebrowsing-disable-auto-update",
                                              "--disable-background-timer-throttling",
                                              "--disable-renderer-backgrounding",
                                              "--disable-features=TranslateUI,site-per-process"
                                          ]
                                         )
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                                             "Chrome/122.0.0.0 Safari/537.36")
        # Block images, fonts, and media
        async def block_resources(route, request):
            if request.resource_type in ["image", "media", "font"]:
                await route.abort()
            else:
                await route.continue_()

        page = await context.new_page()
        await page.route("**/*", block_resources)
        await page.goto(url, wait_until="load")
        html = await page.content()
        #with open(isin + '.html', "w") as f:
        #    f.write(html)
        # print(html)
        await page.close()
        await context.close()
        await browser.close()
        return html
'''