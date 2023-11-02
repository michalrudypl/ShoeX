"""Analyze results of scraping."""
from typing import List

import pandas as pd
import requests

from logger_module import get_logger


class Analyzer:
    """Analyzer class."""

    def __init__(self, df: pd.DataFrame) -> None:
        """Initialize the Analyzer with a DataFrame."""
        self.logging = get_logger(self.__class__.__name__)
        self.df = df
        self.transaction_fee = 0.09
        self.payment_proc = 0.03
        self._usd_to_pln: float = 4.0

    @property
    def usd_to_pln(self) -> float:
        """Lazy-load USD to PLN conversion rate."""
        if self._usd_to_pln is None:
            try:
                api = "http://api.nbp.pl/api/exchangerates/rates/A/USD/"
                r = requests.get(api, timeout=10)
                r.raise_for_status()
                self._usd_to_pln = float(r.json()["rates"][0]["mid"])
            except requests.RequestException:
                self.logging.warning("Error fetching exchange rate, defaulting to 4.")
        return self._usd_to_pln

    def usd_prices_to_pln(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Convert given columns from USD to PLN."""
        df = df.copy()
        for column in columns:
            df[column] = (df[column] * self.usd_to_pln).apply(float).round(2)
        return df

    def format_df(self) -> pd.DataFrame:
        """Format the DataFrame for analysis."""
        df = self.df.dropna(subset=["id"]).copy()
        cols_to_format = [
            "averageDeadstockPrice",
            "highestBid",
            "lowestAsk",
            "volatility",
            "lastSale",
        ]
        df = self.usd_prices_to_pln(df, cols_to_format)

        delivery_cost_usd = 5.45
        df["finalPriceAfterTaxes"] = (
            df["averageDeadstockPrice"]
            - df["averageDeadstockPrice"] * self.payment_proc
            - df["averageDeadstockPrice"] * self.transaction_fee
            - delivery_cost_usd * self.usd_to_pln
        ).round(2)

        df["profitOrLoss"] = df["finalPriceAfterTaxes"] - df["price"]
        return df

    def analyze(self) -> pd.DataFrame:
        """Perform the analysis and return filtered DataFrame."""
        df = self.format_df()

        filter_conditions = (
            (df["profitOrLoss"] > 50)
            & (df["numberOfBids"] > 0)
            & (df["volatility"] < 1)
        )

        filtered_df = df[filter_conditions]
        self.logging.info(f"Found {len(filtered_df)} profitable opportunities.")

        return filtered_df
