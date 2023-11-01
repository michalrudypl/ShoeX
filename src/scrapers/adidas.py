"""Adidas scraper."""
import logging
from queue import Queue

import pandas as pd
import requests

from ._base_scraper import BaseScraper

# Initialize logging
logging.basicConfig(level=logging.INFO)


class Adidas(BaseScraper):
    """Adidas scraper."""

    def __init__(self) -> None:
        logging.info("Initializing Adidas scraper.")
        super().__init__()
        self.url = "https://www.adidas.pl/api/plp/content-engine"
        self.dfs: list = []
        self.headers[
            "user-agent"
        ] = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"  # noqa: E501
        del self.headers["accept-language"]
        self.queries = ("mezczyzni-buty", "kobiety-buty")
        self.params = {
            "experiment": "CORP_BEN",
            "query": "mezczyzni-buty",
        }
        self.start = 0

    def parse(self, response: requests.Response) -> pd.DataFrame:
        logging.info("Parsing response.")

        try:
            products = response.json()["raw"]["itemList"]["items"]
        except Exception as e:
            logging.error(f"Failed to parse JSON from response: {e}")
            return pd.DataFrame()

        if len(products) <= 0:
            logging.warning("No products found in the response.")
            return pd.DataFrame()

        data: dict = {"id": [], "price": [], "link": []}

        for product in products:
            try:
                data["id"].append(product["modelId"])
                data["price"].append(product["salePrice"])
                data["link"].append("https://www.adidas.pl/" + product["link"])
            except KeyError as e:
                logging.error(f"Missing key in product data: {e}")

        return pd.DataFrame(data)

    def run(self, queue: Queue) -> None:
        logging.info(f"Start scraping {self.__class__.__name__}")

        for query in self.queries:
            logging.info(f"Scraping query: {query}")
            self.params["query"] = query
            while True:
                self.params["start"] = self.start
                df = self.parse(self._get(params=self.params))

                if df.empty is False:
                    self.dfs.append(df)
                    self.start += 48
                else:
                    logging.info(f"Reached the end of query: {query}")
                    break

        df_concated = pd.concat(self.dfs)
        self.save_file(df_concated, self.__class__.__name__)

        if queue is not None:
            queue.put((self.__class__.__name__, df_concated))
            logging.info("Data added to the queue.")
