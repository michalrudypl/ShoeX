"""Module for scraping data from StockX."""

import json
import time
from multiprocessing.managers import DictProxy

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class StockX:
    """A scraper for fetching shoe data from StockX."""

    def __init__(self, query: str = "jordan", results_per_page: str = "1000"):
        """Initialize the scraper with query parameters."""
        self.query = query
        self.results_per_page = results_per_page
        self.driver = None

    def get_data(self) -> dict:
        """Fetch data from the StockX API."""
        url = f"https://stockx.com/api/browse?_search={self.query}&resultsPerPage={self.results_per_page}"
        print(f"Fetching data from: {url}")

        self.driver.get(url)
        time.sleep(2)  # Allow 2 seconds for the page to load

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        json_data = soup.find("pre").text

        return json.loads(json_data)

    def loop_data(self, data) -> pd.DataFrame:
        """Loop through the data to create a DataFrame."""
        product_list = []

        for product in data["Products"]:
            product_info = {
                "Title": product["title"],
                "shoeId": product["styleId"],
                "LowestAsk": product["market"]["lowestAsk"],
                "NumberOfAsks": product["market"]["numberOfAsks"],
                "LastSale": product["market"]["lastSale"],
                "lowestAskSize": product["market"]["lowestAskSize"],
                "numberOfAsks": product["market"]["numberOfAsks"],
                "hasAsks": product["market"]["hasAsks"],
                "salesThisPeriod": product["market"]["salesThisPeriod"],
                "salesLastPeriod": product["market"]["salesLastPeriod"],
                "highestBid": product["market"]["highestBid"],
                "highestBidSize": product["market"]["highestBidSize"],
                "numberOfBids": product["market"]["numberOfBids"],
                "hasBids": product["market"]["hasBids"],
                "annualHigh": product["market"]["annualHigh"],
                "annualLow": product["market"]["annualLow"],
                "deadstockRangeLow": product["market"]["deadstockRangeLow"],
                "deadstockRangeHigh": product["market"]["deadstockRangeHigh"],
                "volatility": product["market"]["volatility"],
                "deadstockSold": product["market"]["deadstockSold"],
                "pricePremium": product["market"]["pricePremium"],
                "averageDeadstockPrice": product["market"]["averageDeadstockPrice"],
                "lastSale": product["market"]["lastSale"],
                "lastSaleSize": product["market"]["lastSaleSize"],
                "salesLast72Hours": product["market"]["salesLast72Hours"],
                "changeValue": product["market"]["changeValue"],
                "changePercentage": product["market"]["changePercentage"],
                "absChangePercentage": product["market"]["absChangePercentage"],
                "totalDollars": product["market"]["totalDollars"],
                "lastLowestAskTime": product["market"]["lastLowestAskTime"],
                "lastHighestBidTime": product["market"]["lastHighestBidTime"],
                "lastSaleDate": product["market"]["lastSaleDate"],
                "deadstockSoldRank": product["market"]["deadstockSoldRank"],
            }
            product_list.append(product_info)

        df = pd.DataFrame(product_list)
        return df

    def run(self, manager_dict: DictProxy = None) -> pd.DataFrame:
        """Main runner function for the scraper."""
        with webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())
        ) as self.driver:
            data = self.get_data()
            df_concated = self.loop_data(data)

        if manager_dict is not None:
            manager_dict[self.__class__.__name__] = df_concated

        return df_concated
