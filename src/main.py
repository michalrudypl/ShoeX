"""Main runner for the scraper application."""

import threading
from queue import Queue
from typing import Dict, Tuple

import pandas as pd

from scrapers.adidas import Adidas
from scrapers.eobuwie import Eobuwie
from scrapers.nike import Nike
from scrapers.stockx import StockX
from shoes_purchase_analyzer import Analyzer

# Initialize scraper instances
scrapers = (StockX(), Nike(), Eobuwie(), Adidas())


def run_scrapers() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run all scraper instances in separate threads.
    Collect their DataFrame results in a queue.
    Return DataFrames for StockX and other scrapers.
    """
    dfs_queue: Queue = Queue()

    # Start threads for each scraper
    threads = [threading.Thread(target=s.run, args=(dfs_queue,)) for s in scrapers]
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect DataFrames from queue into a dictionary
    dfs_dict: Dict[str, pd.DataFrame] = {}
    while not dfs_queue.empty():
        name, df = dfs_queue.get()
        dfs_dict[name] = df

    # Separate StockX DataFrame from other scrapers
    df_stockx = dfs_dict.get("StockX")
    df_scrapers = pd.concat([df for name, df in dfs_dict.items() if name != "StockX"])

    return df_stockx, df_scrapers


def merge_dataframes(
    df_stockx: pd.DataFrame, df_scrapers: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge StockX DataFrame with other scrapers' DataFrames.
    """
    return df_stockx.merge(df_scrapers, how="left", left_on="styleId", right_on="id")


def main() -> None:
    """
    Main function to run scraper threads, merge DataFrames, and analyze results.
    """
    df_stockx, df_scrapers = run_scrapers()
    df_merged = merge_dataframes(df_stockx, df_scrapers)

    analyzer = Analyzer(df_merged)
    df_analyzed = analyzer.analyze()
    df_analyzed.to_excel("result.xlsx", index=False)


if __name__ == "__main__":
    main()
