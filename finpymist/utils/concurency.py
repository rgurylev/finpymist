
import asyncio
import logging

logger = logging.getLogger(__name__)

async def foo():
    return None

def paginate(items, page_size, page_number):
    """Returns a slice of the list for the given page number and page size."""
    start = (page_number - 1) * page_size
    end = start + page_size
    return items[start:end]

async def async_method(obj, method_name, *args, **kwargs):
    try:
        method = getattr(obj, method_name)
    except Exception as e:
        logger.error(f"Failed {repr(e)}")
        return await foo()
    if callable(method):
        return await method(*args, **kwargs)
    else:
        logger.error (f"{method_name} is not a callable method")
        return await foo()

async def execute_method(items, page_size = 1, method_name = None, *args, **kwargs):
    total_pages = (len(items) + page_size - 1) // page_size
    for page_number in range(1, total_pages + 1):
        page = paginate(items, page_size, page_number)
        tasks = [async_method(obj, method_name, *args, **kwargs ) for obj in page]
        _ = await asyncio.gather(*tasks)

async def execute_func(items, page_size = 1, delay = 0, func_name = None, *args, **kwargs):
    total_pages = (len(items) + page_size - 1) // page_size
    result = []
    for page_number in range(1, total_pages + 1):
        page = paginate(items, page_size, page_number)
        tasks = [func_name (obj) for obj in page]
        r = await asyncio.gather(*tasks)
        result += r
        await asyncio.sleep (delay)
    return result

async def execute_tasks (tasks, page_size=1):
    total_pages = (len(tasks) + page_size - 1) // page_size
    for page_number in range(1, total_pages + 1):
        tasks_ = paginate(tasks, page_size, page_number)
        for future in asyncio.as_completed(tasks_):
            result = await future
            yield result

