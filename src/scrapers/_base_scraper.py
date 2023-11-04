"""BaseScraper module for common scraper functionalities."""

import abc
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests


class BaseScraper(abc.ABC):
    """Abstract class for web scraping."""

    def __init__(self) -> None:
        self.headers = {
            "accept": "application/json",
            "accept-encoding": "utf-8",
            "accept-language": "en-GB,en;q=0.9",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",  # noqa: E501
            "x-requested-with": "XMLHttpRequest",
            "app-platform": "Iron",
            "app-version": "2022.05.08.04",
        }
        self.url: str = ""
        self._session = requests.session()

    @abc.abstractmethod
    def run(self) -> Any:
        """Abstract method for running the scraper."""
        pass

    @staticmethod
    def save_file(df: pd.DataFrame, file_name: str) -> None:
        """Saving files."""
        xlsx_results_path = Path("xlsx_results")

        if os.path.exists(xlsx_results_path) is False:
            os.makedirs(xlsx_results_path)

        logging.info(f"Saving file: {file_name}")

        saving_path = Path(xlsx_results_path / f"{file_name}.xlsx")
        df.to_excel(saving_path, index=False)

    def _get(self, params: dict) -> requests.Response:
        """Perform GET request and handle exceptions."""
        try:
            r = self._session.get(
                self.url, params=params, headers=self.headers, timeout=10
            )
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as errh:
            logging.error("HTTP Error: %s", errh)
            raise requests.exceptions.HTTPError
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise requests.exceptions.ConnectionError
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise requests.exceptions.Timeout
        except requests.exceptions.RequestException as err:
            logging.error("Unknown Error: %s", err)
            raise requests.exceptions.RequestException
