import threading
from queue import Queue

import pandas as pd

from scrapers.adidas import Adidas
from scrapers.eobuwie import Eobuwie
from scrapers.nike import Nike
from scrapers.stockx import StockX
from shoes_purchase_analyzer import Analyzer

scrapers = (
    StockX(),
    Nike(),
    Eobuwie(),
    Adidas(),
)


def run_scrapers() -> tuple:
    """Run all scrapers and store the data in the manager."""
    dfs_queue = Queue()

    threads = [threading.Thread(target=s.run, args=(dfs_queue,)) for s in scrapers]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    dfs_dict = {}
    while not dfs_queue.empty():
        name, df = dfs_queue.get()
        dfs_dict[name] = df

    df_stockx = dfs_dict["StockX"]
    df_scrapers = pd.concat([v for k, v in dfs_dict.items() if k != "StockX"])

    return (df_stockx, df_scrapers)


def merge_dataframes(
    df_stockx: pd.DataFrame, df_scrapers: pd.DataFrame
) -> pd.DataFrame:
    """Merging dfs."""
    return df_stockx.merge(df_scrapers, how="left", left_on="styleId", right_on="id")


def main() -> None:
    """Main function."""
    df_stockx, df_scrapers = run_scrapers()

    df_merged = merge_dataframes(df_stockx, df_scrapers)

    analyzer = Analyzer(df_merged)
    df_analyzed = analyzer.analyze()
    df_analyzed.to_excel("result.xlsx", index=False)


if __name__ == "__main__":
    main()
