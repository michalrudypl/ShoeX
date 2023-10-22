"""Main shoex file."""
import logging
import multiprocessing
from multiprocessing import Manager, Process

import pandas as pd

from scrapers.adidas import Adidas
from scrapers.eobuwie import Eobuwie
from scrapers.nike import Nike
from scrapers.stockx import StockX
from shoes_purchase_analyzer import Analyzer

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATEFMT = "%d-%b-%y %H:%M:%S"
LOG_FILENAME = "app.log"


def configure_logging() -> None:
    """Configure the logger."""
    logging.basicConfig(
        filename=LOG_FILENAME,
        filemode="w",
        format=LOG_FORMAT,
        level=logging.DEBUG,
        datefmt=LOG_DATEFMT,
    )


selenium_scrapers = StockX()

scrapers = (
    Nike(),
    Eobuwie(),
    Adidas(),
)


def run_scrapers(manager: multiprocessing.managers.SyncManager) -> tuple:
    """Run all scrapers and store the data in the manager."""
    dfs_manager = manager.dict()

    dfs_manager["StockX"] = selenium_scrapers.run()

    processes = [Process(target=s.run, args=(dfs_manager,)) for s in scrapers]

    for process in processes:
        process.start()
    for process in processes:
        process.join()

    df_stockx = dfs_manager["StockX"]
    df_scrapers = pd.concat([v for k, v in dfs_manager.items() if k != "StockX"])

    return (df_stockx, df_scrapers)


def merge_dataframes(
    df_stockx: pd.DataFrame, df_scrapers: pd.DataFrame
) -> pd.DataFrame:
    """Merging dfs."""
    return df_stockx.merge(df_scrapers, how="left", left_on="styleId", right_on="id")


def main() -> None:
    """Main function."""
    configure_logging()
    logging.info("Start program")

    with Manager() as manager:
        df_stockx, df_scrapers = run_scrapers(manager)

        df_merged = merge_dataframes(df_stockx, df_scrapers)

        analyzer = Analyzer(df_merged)
        df_analyzed = analyzer.analyze()
        df_analyzed.to_excel("result.xlsx", index=False)


if __name__ == "__main__":
    main()
