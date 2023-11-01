"""Adidas scraper."""
import logging
from queue import Queue

import pandas as pd
import requests

from ._base_scraper import BaseScraper


class Adidas(BaseScraper):
    """Adidas scraper."""

    def __init__(self) -> None:
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
        products = response.json()["raw"]["itemList"]["items"]

        if len(products) <= 0:
            return pd.DataFrame()

        data: dict = {"id": [], "price": [], "link": []}

        for product in products:
            data["id"].append(product["modelId"])
            data["price"].append(product["salePrice"])
            data["link"].append("https://www.adidas.pl/" + product["link"])

        return pd.DataFrame(data)

    def run(self, queue: Queue) -> None:
        logging.info("Start scraping %s", self.__class__.__name__)

        for query in self.queries:
            self.params["query"] = query
            while True:
                self.params["start"] = self.start

                df = self.parse(self._get(params=self.params))

                if df.empty is False:
                    self.dfs.append(df)
                    self.start += 48
                else:
                    break

        df_concated = pd.concat(self.dfs)

        if queue is not None:
            queue.put((self.__class__.__name__, df_concated))
