import asyncio
import pandas as pd
import logging
import set_logger
from finpymist.bonds import bonds

logger = logging.getLogger(__name__)

async def main():
    b = await bonds()
    #s = ''
    #for x in sorted (b, key=lambda x: -x.rate):
    #    s += f"{x.name} \n" f"дней: {x.days} ставка:{x.rate*100:6.2f}\n\n"
    #print(s)
    df = pd.DataFrame(sorted (b, key=lambda x: -x.rate))
    df.to_excel("E:\\dev\\PycharmProjects\\finpymist\\bonds.xlsx")

if __name__ == "__main__":
    asyncio.run( main())
