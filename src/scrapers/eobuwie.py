"""Eobuwie scraper."""
import logging
from queue import Queue

import pandas as pd
import requests

from ._base_scraper import BaseScraper

# Initialize logging
logging.basicConfig(level=logging.INFO)


class Eobuwie(BaseScraper):
    """Eobuwie scraper."""

    def __init__(self) -> None:
        """Init."""
        super().__init__()
        logging.info("Initializing Eobuwie scraper.")
        self.url = "https://eobuwie.com.pl/t-api/rest/search/eobuwie/v5/search_web"
        self.dfs: list = []
        self.categories = (
            "meskie/polbuty/sneakersy",
            "damskie/polbuty/sneakersy",
        )
        self.params = {
            "channel": "eobuwie",
            "currency": "PLN",
            "locale": "pl_PL",
            "limit": 72,
            "page": 1,
            "categories[]": "meskie/polbuty/sneakersy",
            "select[]": [
                "product_active",
                "product_badge",
                "final_price",
                "model",
                "url_key",
                "pl_PL",
            ],
        }

    @staticmethod
    def parse_model(value: str) -> str:
        """Parse model."""
        model_list = value.split()
        if len(model_list[-1]) < 5 and len(model_list) > 2:
            return model_list[-2] + "-" + model_list[-1]
        return model_list[-1]

    def parse(self, response: requests.Response) -> pd.DataFrame:
        """Parsing."""
        logging.info("Parsing response.")

        try:
            products = response.json()["products"]
        except Exception as e:
            logging.error(f"Failed to parse JSON from response: {e}")
            return pd.DataFrame()

        if len(products) <= 0:
            logging.warning("No products found in the response.")
            return pd.DataFrame()

        data: dict = {"id": [], "price": [], "link": []}

        for product in products:
            try:
                data["id"].append(self.parse_model(product["values"]["model"]["value"]))
                data["price"].append(
                    product["values"]["final_price"]["value"]["pl_PL"]["PLN"]["amount"]
                )
                data["link"].append(
                    "https://eobuwie.com.pl/p/"
                    + product["values"]["url_key"]["value"]["pl_PL"]
                )
            except KeyError as e:
                logging.error(f"Missing key in product data: {e}")

        return pd.DataFrame(data)

    def run(self, queue: Queue) -> None:
        logging.info(f"Start scraping {self.__class__.__name__}")

        for category in self.categories:
            logging.info(f"Scraping category: {category}")
            self.params["categories[]"] = category
            while True:
                df = self.parse(self._get(params=self.params))
                if df.empty is False:
                    self.dfs.append(df)
                    self.params["page"] += 1
                else:
                    logging.info(f"Reached the end of category: {category}")
                    break

        df_concated = pd.concat(self.dfs)

        self.save_file(df_concated, self.__class__.__name__)

        if queue is not None:
            queue.put((self.__class__.__name__, df_concated))
            logging.info("Data added to the queue.")
