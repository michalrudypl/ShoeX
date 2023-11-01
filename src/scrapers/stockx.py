"""StockX scraper module."""

import json
import time
from queue import Queue
from typing import Dict

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class StockX:
    """Scraper for fetching shoe data from StockX."""

    def __init__(self, query: str = "jordan", results_per_page: str = "1000"):
        """Initialize the scraper with search parameters."""
        self.query = query
        self.results_per_page = results_per_page
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())
        )

    def get_data(self) -> Dict:
        """Fetch the raw data from the StockX API."""
        url = f"https://stockx.com/api/browse?_search={self.query}&resultsPerPage={self.results_per_page}"
        self.driver.get(url)
        time.sleep(2)  # Allow the page to load
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        json_data = soup.find("pre").text

        return json.loads(json_data)

    def loop_data(self, data: Dict) -> pd.DataFrame:
        """Parse the raw data to create a DataFrame."""
        product_list = [
            {key: product["market"].get(key, None) for key in product["market"]}
            for product in data["Products"]
        ]
        return pd.DataFrame(product_list)

    def run(self, queue: Queue) -> None:
        """Main function that orchestrates the scraping process."""
        data = self.get_data()
        df = self.loop_data(data)

        if queue is not None:
            queue.put((self.__class__.__name__, df))

        self.driver.close()
