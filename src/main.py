import requests
from bs4 import BeautifulSoup


def get_data():
    session = requests.Session()
    for i in range(1, 333):
        url = f"https://www.argcollectibles.com/categoria-producto/billetes/page/{i}/"
        try:
            response = session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            products = soup.find_all(
                "div", class_="box-text box-text-products text-center grid-style-2"
            )
            print(f"currently in page {i}")

            for product in products:
                title_element = product.find("a", class_="woocommerce-LoopProduct-link")
                title = (
                    title_element.text.strip() if title_element else "No title found"
                )

                price_element = product.find("span", class_="price")
                if price_element:
                    amount = price_element.find("bdi")
                    price = amount.text if amount else ""
                else:
                    price = "No price found"

                print(f"Title: {title}")
                print(f"Price: {price}")
                print("-" * 50)

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    get_data()
