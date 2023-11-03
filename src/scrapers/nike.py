"""Nike scraper module."""
from queue import Queue
from typing import Dict, List, Optional, Union

import pandas as pd
import requests

from logger_module import get_logger

from ._base_scraper import BaseScraper


class Nike(BaseScraper):
    """
    A scraper for Nike products.
    """

    def __init__(self) -> None:
        super().__init__()
        self.logging = get_logger(self.__class__.__name__)
        self.logging.info("Initializing Nike scraper.")
        self.url: str = "https://api.nike.com/cic/browse/v2"
        self.dfs: List[pd.DataFrame] = []  # List to store data frames
        self.common_params: Dict[str, str] = {
            "queryid": "products",
            "anonymousId": "AA0CFA5C8E52CA284E0B58B1F25BC32C",
            "country": "pl",
            "language": "pl",
            "localizedRangeStr": "{lowestPrice} – {highestPrice}",
        }
        self.attribute_ids: tuple = (
            "16633190-45e5-4830-a068-232ac7aea82c,7baf216c-acc6-4452-9e07-39c2ca77ba32",  # women shoes
            "0f64ecc7-d624-4e91-b171-b83a03dd8550,16633190-45e5-4830-a068-232ac7aea82c",  # men shoes
        )

    def parse(self, response: requests.Response) -> pd.DataFrame:
        """Parsing."""
        self.logging.info("Parsing Nike data.")
        data: Dict[str, List[str]] = {"id": [], "price": [], "link": []}
        products: List[Dict[str, Union[str, Dict]]] = (
            response.json().get("data", {}).get("products", {}).get("products", [])
        )

        if not products:
            self.logging.warning("No products found.")
            return pd.DataFrame()

        for product in products:
            if product["inStock"] and product["productType"] == "FOOTWEAR":
                product_id = product["url"].split("/")[-1]
                product_price = product["price"]["currentPrice"]
                product_link = f"https://www.nike.com/pl/{product['url'][14:]}"

                data["id"].append(product_id)
                data["price"].append(product_price)
                data["link"].append(product_link)

        self.logging.info("Parsing completed.")
        return pd.DataFrame(data)

    def create_endpoint(self, attribute: str, anchor: int) -> str:
        """
        Creating endpoint.
        """
        self.logging.info("Creating endpoint for Nike API.")
        endpoint_path = (
            f"/product_feed/rollup_threads/v2?filter=marketplace(PL)&"
            f"filter=language(pl)&filter=employeePrice(true)&"
            f"filter=attributeIds({attribute})&anchor={anchor}&"
            f"consumerChannelId=d9a5bc42-4b9c-4976-858a-f159cf99c647&count=24"
        )
        return endpoint_path

    def run(self, queue: Optional[Queue] = None) -> None:
        self.logging.info("Start scraping %s", self.__class__.__name__)
        anchor: int = 0

        for attribute in self.attribute_ids:
            while True:
                endpoint_path = self.create_endpoint(attribute, anchor)
                params = {**self.common_params, "endpoint": endpoint_path}
                response = self._get(params=params)

                df = self.parse(response)
                if not df.empty:
                    self.dfs.append(df)
                    anchor += 24
                else:
                    self.logging.info("No more data to fetch, breaking the loop.")
                    break

        self.logging.info("Nike scraping completed.")

        df_concated = pd.concat(self.dfs)
        self.save_file(df_concated, self.__class__.__name__)

        if queue:
            queue.put((self.__class__.__name__, df_concated))
            self.logging.info("Data added to queue.")
