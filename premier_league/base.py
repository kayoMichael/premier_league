import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from http.client import HTTPException
from pathlib import Path
from typing import Optional, Union
from xml.etree import ElementTree

import requests
import requests_cache
from bs4 import BeautifulSoup
from lxml import etree
from requests import Response, Session
from tqdm import tqdm

from premier_league.utils.methods import clean_xml_text
from premier_league.utils.threading import threaded


@dataclass
class BaseScrapper:
    """
    A base class for web scraping operations.

    This class provides methods for making HTTP requests, parsing HTML content,
    and extracting data using XPath queries.

    Attributes:
        url (str): The URL to scrape. The URL can contain placeholders for the season.
        page (ElementTree): The parsed XML representation of the web page.
        season (str): The processed season for scraping data.
        target_season (str): The target season (parameter) for scraping data.
        cache (bool): Whether to cache the HTTP requests. Defaults to True.
        season_limit (int): The lower limit for the season. Defaults to 1992.
        expire_cache (int): The expiry time for the cache in seconds. Defaults to 7200.
        session (Union[requests_cache.CachedSession, requests]): The requests session object.
    """

    url: str
    requires_season: bool = True
    page: ElementTree = field(default_factory=lambda: None, init=False)
    season: str = field(default=None, init=False)
    target_season: str = field(default=None)
    cache: bool = field(default=True)
    season_limit: int = field(default=1992)
    expire_cache: int = field(default=7200)
    session: Union[requests_cache.CachedSession, Session] = field(
        default=None, init=False
    )

    def __post_init__(self):
        """
        Initialize the current and previous seasons based on the current date or target season.

        Raises:
            ValueError: If the target_season is invalid or in an incorrect format.
        """
        if not self.requires_season:
            return

        if self.cache:
            self.session = requests_cache.CachedSession(
                "prem_cache", expire_after=self.expire_cache
            )
        else:
            self.session = requests.session()

        current_date = datetime.now()
        if not self.target_season:
            current_year = current_date.year
            current_month = current_date.month
            if current_month >= 8:
                self.season = (
                    f"{current_year}-{str(current_year + 1)[2:]}"
                    if self.url[-1] != "/"
                    else f"{current_year}-{str(current_year + 1)}"
                )
            else:
                self.season = (
                    f"{current_year - 1}-{str(current_year)[2:]}"
                    if self.url[-1] != "/"
                    else f"{current_year - 1}-{str(current_year)}"
                )
        else:
            if not re.match(r"^\d{4}-\d{4}$", self.target_season):
                raise ValueError(
                    "Invalid format for target_season. Please use 'YYYY-YYYY' (e.g., '2024-2025') with a regular hyphen."
                )
            elif int(self.target_season[:4]) > current_date.year:
                raise ValueError("Invalid target_season. It cannot be in the future.")
            elif int(self.target_season[:4]) < self.season_limit:
                raise ValueError(
                    f"Invalid target_season. This Class only supports seasons after {self.season_limit}/{self.season_limit + 1}. It cannot be before {self.season_limit}."
                )
            if self.url[-1] != "/":
                self.season = f"{self.target_season[:4]}-{self.target_season[7:]}"
            else:
                self.season = self.target_season

        self.url = self.url.replace("{SEASON}", self.season)

    def make_request(self) -> Response:
        """
        Make an HTTP GET request to the specified URL.

        Returns:
            Response: The HTTP response object.

        Raises:
            HTTPException: If an error occurs during the request.
        """
        try:
            response: Response = self.session.get(
                url=self.url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/113.0.0.0 "
                        "Safari/537.36"
                    ),
                },
            )
            return response
        except Exception as e:
            raise HTTPException(f"An error occurred: {e} for url: {self.url}")

    def parse_to_html(self):
        """
        Parse the HTTP response content into a BeautifulSoup object.

        Returns:
            BeautifulSoup: The parsed HTML content.
        """
        response: Response = self.make_request()
        return BeautifulSoup(markup=response.content, features="html.parser")

    def clear_cache(self):
        """
        Clear the cache for the current session.
        """
        self.session.cache.clear()

    @staticmethod
    def convert_to_xml(bsoup: BeautifulSoup):
        """
        Convert a BeautifulSoup object to a lxml ElementTree.

        Args:
            bsoup (BeautifulSoup): The BeautifulSoup object to convert.

        Returns:
            ElementTree: The converted XML tree.
        """
        return etree.HTML(bsoup.encode())

    @staticmethod
    def additional_scrapper(additional_url: str, cache: Optional[bool] = True):
        """
        Create a new BaseScrapper instance for an additional URL without creating a new object.

        Args:
            additional_url (str): The URL to scrape.
            cache (bool): Whether to cache the HTTP requests. Defaults to True.

        Returns:
            BaseScrapper: A new BaseScrapper instance with the page loaded.
        """
        scrapper = BaseScrapper(url=additional_url, requires_season=False, cache=cache)
        scrapper.page = BaseScrapper.request_url_page(scrapper)
        return scrapper

    def request_url_page(self) -> ElementTree:
        """
        Request the URL and parse it into an XML ElementTree.

        Returns:
            ElementTree: The parsed XML representation of the web page.
        """
        bsoup: BeautifulSoup = self.parse_to_html()
        return self.convert_to_xml(bsoup=bsoup)

    def get_list_by_xpath(
        self, xpath: str, clean: Optional[bool] = True
    ) -> Optional[list]:
        """
        Get a list of elements matching the given XPath.

        Args:
            xpath (str): The XPath query to execute.
            clean (bool, optional): Whether to clean the text content of the elements. Defaults to True.

        Returns:
            Optional[list]: A list of matching elements, or an empty list if no matches are found.
        """
        elements: list = self.page.xpath(xpath)
        if clean:
            elements_valid: list = [
                clean_xml_text(e) for e in elements if clean_xml_text(e)
            ]
        else:
            elements_valid: list = [e for e in elements]
        return elements_valid or []

    def get_text_by_xpath(
        self,
        xpath: str,
        pos: int = 0,
        index: Optional[int] = None,
        index_from: Optional[int] = None,
        index_to: Optional[int] = None,
        join_str: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get text content from elements matching the given XPath.

        This method provides various ways to select and manipulate the matched elements.

        Args:
            xpath (str): The XPath query to execute.
            pos (int, optional): The position of the element to return. Defaults to 0.
            index (int, optional): The index of the element to return.
            index_from (int, optional): The starting index for slicing the result list.
            index_to (int, optional): The ending index for slicing the result list.
            join_str (str, optional): A string to join multiple elements if returned.

        Returns:
            Optional[str]: The extracted text content, or None if no match is found.
        """
        element = self.page.xpath(xpath)

        if not element:
            return None

        if isinstance(element, list):
            element = [clean_xml_text(e) for e in element if clean_xml_text(e)]

        if isinstance(index, int):
            element = element[index]

        if isinstance(index_from, int) and isinstance(index_to, int):
            element = element[index_from:index_to]

        if isinstance(index_to, int):
            element = element[:index_to]

        if isinstance(index_from, int):
            element = element[index_from:]

        if isinstance(join_str, str):
            return join_str.join([clean_xml_text(e) for e in element])

        try:
            return clean_xml_text(element[pos])
        except IndexError:
            return None


class BaseDataSetScrapper:
    """
    A class for scraping, managing and caching large amounts of data from a given list of URLs. It uses a flatfile
    caching approach for permanent caching of data to prevent data loss when rate limited or throttled.

    This class provides methods for retrieving, processing, and exporting data sets
    from a specified URL. It inherits from the BaseScrapper class.

    Attributes:
        url (list): The List of URL to scrape.
        page (ElementTree): The parsed XML representation of the web page.
    """

    def __init__(self, cache_dir="cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.pages = []

    def fetch_page(
        self, url, pbar, rate_limit, return_html
    ) -> Union[etree.ElementTree, str, None]:
        """
        Fetch a page from the given URL with rate limits and progress bar.

        Args:
            url (str): The URL to fetch.
            pbar (tqdm): The progress bar object.
            rate_limit (int): The rate limit for requests in seconds.
            return_html (bool): Whether to return the HTML content as a string.
        """
        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 "
                        "Safari/537.36"
                    ),
                },
            )

            if response.status_code == 429:
                print(f"Rate limited on {url}. Exiting...")
                exit(1)
            if response.status_code != 200:
                print(f"Error status {response.status_code} for {url}")
                return None

            html = response.text
            pbar.update(1)
            time.sleep(rate_limit)
            return etree.HTML(html) if return_html else html

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_and_process_all(
        self,
        urls,
        rate_limit=1,
        return_html=True,
        desc="Scraping Progress",
        process_func=None,
    ) -> list:
        """
        Scrape and process all URLs in the list with rate limits.

        Args:
            urls (list): The list of URLs to scrape.
            rate_limit (int, optional): The rate limit for requests in seconds. Defaults to 1.
            return_html (bool, optional): Whether to return the HTML content as a string. Defaults to True.
            desc (str, optional): The description for the progress bar. Defaults to "Scraping Progress".
            process_func (Callable, optional): The function to process the results. Defaults to None.
        """
        results = []
        with tqdm(total=len(urls), desc=desc) as pbar:
            for url in urls:
                result = self.fetch_page(url, pbar, rate_limit, return_html)
                if process_func:
                    result = process_func(result, url=url)
                if result is not None:
                    results.append(result)
        return results

    @threaded(show_progress=True)
    def get_list_by_xpath(
        self,
        page: ElementTree,
        xpath: str,
        clean: Optional[bool] = True,
        show_progress=True,
    ) -> Optional[list]:
        """
        Get a list of elements matching the given XPath.

        Args:
            page (ElementTree): The parsed XML representation of the web page.
            xpath (str): The XPath query to execute.
            clean (bool, optional): Whether to clean the text content of the elements. Defaults to True.
            show_progress (bool, optional): Whether to show a progress bar. Defaults to True.

        Returns:
            Optional[list]: A list of matching elements, or an empty list if no matches are found.
        """
        elements: list = page.xpath(xpath)
        if clean:
            elements_valid: list = [
                clean_xml_text(e) for e in elements if clean_xml_text(e)
            ]
        else:
            elements_valid: list = [e for e in elements]
        return elements_valid or []

    def process_xpath(
        self,
        xpath: str,
        clean: Optional[bool] = True,
        add_str: Optional[str] = None,
        desc: Optional[str] = None,
        flatten=True,
        show_progress=True,
    ) -> list:
        """
        Get a list of elements matching the given XPath using a ThreadPoolExecutor.

        Args:
            xpath (str): The XPath query to execute.
            clean (bool, optional): Whether to clean the text content of the elements. Defaults to True.
            add_str (str, optional): A string to add to the beginning of each element. Defaults to None.
            desc (str, optional): The description for the progress bar. Defaults to None.
            flatten (bool, optional): Whether to flatten the results into a single list. Defaults to True.
            show_progress (bool, optional): Whether to show a progress bar. Defaults to True.

        Returns:
            Optional[list]: A list of matching elements, or an empty list if no matches are found.
        """
        results = self.get_list_by_xpath(
            self.pages, xpath=xpath, clean=clean, show_progress=show_progress
        )

        if flatten:
            if add_str:
                return [f"{add_str}{item}" for sublist in results for item in sublist]
            return [item for sublist in results for item in sublist]
        else:
            return results
