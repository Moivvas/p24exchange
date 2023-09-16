import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
import logging

urls = []
main_list = []

logging.basicConfig(level=logging.ERROR)

try:
    sys_input = sys.argv[1]
except IndexError as e:
    logging.error("You need to type a number to see currency: 'python p24ex.py <number>'")
    sys.exit()

def check_sys_input() -> int:
    if sys_input:
        try:
            sys_input_int = int(sys_input)
            if sys_input_int <= 10:
                return sys_input_int
            else:
                print("You can get currency only for the past 10 days")
                return 0
        except ValueError:
            print("You need to type a number to see currency: 'python p24ex.py <number>'")
            return 0
    else:
        sys_input_int = 1
        return sys_input_int

def urls_creator(days: int) -> list:
    base_url = "https://api.privatbank.ua/p24api/exchange_rates?date="
    
    n = 0
    
    while n < days:
        date = datetime.now() - timedelta(days=n)
        date_str = date.strftime('%d.%m.%Y')
        url = base_url + date_str
        urls.append(url)
        n += 1
    
    return urls

async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f"Error status {response.status} for {url}")
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Connection error {url}: {e}")
        return None

desired_currencies = ["EUR", "USD"]

async def get_exchange():
    tasks = [request(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    for res in responses:
        if res:
            for currency_dict in res["exchangeRate"]:
                if currency_dict["currency"] in desired_currencies:
                    result = {
                        res["date"]: {
                            currency_dict["currency"]: {
                                "saleRate": currency_dict["saleRate"],
                                "purchaseRate": currency_dict["purchaseRate"]
                            }
                        }
                    }
                    main_list.append(result)

async def main():
    sys_input_int = check_sys_input()
    
    if sys_input_int == 0:
        pass

    urls_creator(sys_input_int)
    
    await get_exchange()

    for result in main_list:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
