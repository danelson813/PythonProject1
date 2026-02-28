# PythonProject
import asyncio
import csv
import httpx
from fake_useragent import UserAgent
from selectolax.lexbor import LexborHTMLParser
from helpers.config import load_locators

ua = UserAgent()


def save_csv(list_, filename="data/results.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        keys = list_[0].keys()
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(list_)


semaphore = asyncio.Semaphore(5)


async def fetch_html(url: str, client: httpx.AsyncClient):
    async with semaphore:
        try:
            response = await client.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except httpx.RequestError:
            await asyncio.sleep(1)


def parse_html(html, timeout: int = 30):
    locators = load_locators("locators.toml")
    tree = LexborHTMLParser(html)
    cards = tree.css(locators.card_locators.card_locator)

    results = []
    for card in cards:
        item1_node = card.css_first(locators.item_locators.item1_locator)
        item2_node = card.css_first(locators.item_locators.item2_locator)
        item3_node = card.css_first(locators.item_locators.item3_locator)
        results.append(
            {
                "title": item1_node.attributes["title"] if item1_node else "",
                "price": item2_node.text(strip=True)[1:] if item2_node else "",
                "rating": item3_node.attributes["class"].split()[1]
                if item3_node
                else "",
            }
        )
    return results


async def fetch_n_parse(url: str, client: httpx.AsyncClient):
    html = await fetch_html(url, client)
    items = parse_html(html)
    return items


async def main():
    urls = [f"https://books.toscrape.com/catalogue/page-{i}.html" for i in range(1, 51)]
    async with httpx.AsyncClient() as client:
        tasks = [fetch_n_parse(url, client) for url in urls]
        results = await asyncio.gather(*tasks)
        flat = [item for sublist in results for item in sublist]
        save_csv(flat, filename="data/results.csv")


if __name__ == "__main__":
    asyncio.run(main())
