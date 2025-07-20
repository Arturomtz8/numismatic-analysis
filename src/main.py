import asyncio

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

url = "https://www.argcollectibles.com/categoria-producto/billetes/page/"
products_list = list()


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [get_data(session, url, i) for i in range(1, 333)]
        await asyncio.gather(*tasks, return_exceptions=True)

async def get_data(session, url, page):
    async with session.get(f"{url}{page}/") as response:
        try:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            products = soup.find_all(
                "div", class_="box-text box-text-products text-center grid-style-2"
            )
            print(f"currently in page {page}")

            for product in products:
                title_element = product.find("a", class_="woocommerce-LoopProduct-link")
                title = (
                    title_element.text.strip() if title_element else "No title found"
                )
                link_element = product.find("a", class_="woocommerce-LoopProduct-link")
                link = link_element["href"]
                price_element = product.find("span", class_="price")
                if price_element:
                    amount = price_element.find("bdi")
                    price = amount.text if amount else ""
                else:
                    price = "No price found"

                products_dict = dict()
                products_dict["title"] = title
                products_dict["price"] = price
                products_dict["link"] = link
                products_list.append(products_dict)

            df = pd.DataFrame.from_dict(products_list)
            df.to_csv("billetes.csv", index=False)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
