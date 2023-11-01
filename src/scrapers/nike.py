"""Nike scraper module."""
import logging
from queue import Queue
from typing import Dict, List, Optional, Union

import pandas as pd
import requests

from ._base_scraper import BaseScraper


class NikeScraper(BaseScraper):
    """
    A scraper for Nike products.
    """

    def __init__(self) -> None:
        super().__init__()
        self.base_url: str = "https://api.nike.com/cic/browse/v2"
        self.dfs: List[pd.DataFrame] = []  # List to store data frames
        self.common_params: Dict[str, str] = {
            "queryid": "products",
            "anonymousId": "60DE7E4BCCCD1D7470D10F44D33348F0",
            "country": "pl",
            "language": "pl",
            "localizedRangeStr": "{lowestPrice} – {highestPrice}",
        }
        self.attribute_ids: tuple = (
            "16633190-45e5-4830-a068-232ac7aea82c,7baf216c-acc6-4452-9e07-39c2ca77ba32",  # women shoes
            "0f64ecc7-d624-4e91-b171-b83a03dd8550,16633190-45e5-4830-a068-232ac7aea82c",  # men shoes
        )

    def create_endpoint(self, attribute: str, anchor: int) -> str:
        """Creating endpoint."""
        base_path: str = "/product_feed/rollup_threads/v2?"
        marketplace_filter: str = "filter=marketplace(PL)"
        language_filter: str = "filter=language(pl)"
        employee_price_filter: str = "filter=employeePrice(true)"
        attribute_ids_filter: str = f"filter=attributeIds({attribute})"
        anchor_filter: str = f"anchor={anchor}"
        consumer_channel_id: str = (
            "consumerChannelId=d9a5bc42-4b9c-4976-858a-f159cf99c647"
        )
        count: str = "count=24"

        endpoint: str = (
            f"{base_path}{marketplace_filter}&{language_filter}&{employee_price_filter}&"
            f"{attribute_ids_filter}&{anchor_filter}&{consumer_channel_id}&{count}"
        )
        return endpoint

    def parse(self, response: requests.Response) -> pd.DataFrame:
        data: Dict[str, List[str]] = {"id": [], "price": [], "link": []}
        products: List[Dict[str, Union[str, Dict]]] = (
            response.json().get("data", {}).get("products", {}).get("products", [])
        )

        if not products:
            return pd.DataFrame()

        for product in products:
            if product["inStock"] and product["productType"] == "FOOTWEAR":
                product_id = product["url"].split("/")[-1]
                product_price = product["price"]["currentPrice"]
                product_link = f"https://www.nike.com/pl/{product['url'][14:]}"

                data["id"].append(product_id)
                data["price"].append(product_price)
                data["link"].append(product_link)

        return pd.DataFrame(data)

    def run(self, queue: Optional[Queue] = None) -> None:
        logging.info(f"Start scraping {self.__class__.__name__}")
        anchor: int = 0

        for attribute in self.attribute_ids:
            endpoint: str = self.create_endpoint(attribute, anchor)
            params: Dict[str, str] = {**self.common_params, "endpoint": endpoint}

            while True:
                response: requests.Response = self._get(params=params)
                df: pd.DataFrame = self.parse(response)

                if not df.empty:
                    self.dfs.append(df)
                    anchor += 24
                else:
                    break

        df_concated: pd.DataFrame = pd.concat(self.dfs)

        if queue:
            queue.put((self.__class__.__name__, df_concated))
