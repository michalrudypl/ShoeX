"""BaseScraper module for common scraper functionalities."""

import abc
import logging
from typing import Optional

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

    @abc.abstractmethod
    def run(self) -> None:
        """Abstract method for running the scraper."""
        pass

    @abc.abstractmethod
    def parse(self) -> None:
        """Abstract method for parsing the data."""
        pass

    def _get(self, params: dict) -> Optional[requests.Response]:
        """Perform GET request and handle exceptions."""
        try:
            r = requests.get(
                self.url, params=params, headers=self.headers, timeout=10
            )  # Added timeout
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as errh:
            logging.error("HTTP Error: %s", errh)
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
        except requests.exceptions.RequestException as err:
            logging.error("Unknown Error: %s", err)
        return None  # Return None if there's an exception
