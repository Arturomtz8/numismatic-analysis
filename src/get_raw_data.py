import asyncio
import os

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from prefect import flow, task

from gc_utility.upload_data import upload_csv_to_gcs

BUCKET_NAME = os.getenv("NUMISMATIC_BUCKET")
SOURCE_BLOB_NAME = os.getenv("NUMISMATIC_RAW")
url = "https://www.argcollectibles.com/categoria-producto/billetes/page/"
products_list = list()

# Define a semaphore to limit the number of concurrent requests
# Adjust this value based on how aggressive you want to be
semaphore = asyncio.Semaphore(8)


@flow
async def main():
    """Main flow to orchestrate the scraping process."""
    # Define a custom User-Agent to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # Create a list of tasks, each one getting data for a specific page
        tasks = [get_data(session, url, i) for i in range(1, 10)]

        # Run all tasks concurrently, but the semaphore will limit how many run at the same time
        await asyncio.gather(*tasks, return_exceptions=True)

    # After all tasks are done, save the data to a CSV file
    df = pd.DataFrame.from_dict(products_list)
    df.to_csv("billetes.csv", index=False)
    await upload_csv_to_gcs(BUCKET_NAME, "billetes.csv", SOURCE_BLOB_NAME)


@task(retries=3, retry_delay_seconds=10)
async def get_data(session, url, page):
    """Task to fetch and parse data from a single page."""
    # Use the semaphore to acquire a slot; this will block if the limit is reached
    async with semaphore:
        try:
            # Add a small delay to be polite and avoid server overload
            await asyncio.sleep(1)

            async with session.get(f"{url}{page}/") as response:
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                products = soup.find_all(
                    "div", class_="box-text box-text-products text-center grid-style-2"
                )
                print(f"currently in page {page}")

                for product in products:
                    title_element = product.find(
                        "a", class_="woocommerce-LoopProduct-link"
                    )
                    title = (
                        title_element.text.strip()
                        if title_element
                        else "No title found"
                    )

                    link_element = product.find(
                        "a", class_="woocommerce-LoopProduct-link"
                    )
                    link = link_element["href"] if link_element else "No link found"

                    price_element = product.find("span", class_="price")
                    price = "No price found"
                    if price_element:
                        amount = price_element.find("bdi")
                        price = amount.text if amount else "No price found"

                    products_dict = {"title": title, "price": price, "link": link}
                    products_list.append(products_dict)
        except aiohttp.ClientResponseError as e:
            print(f"HTTP Error on page {page}: {e}")
        except Exception as e:
            print(f"Error on page {page}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
