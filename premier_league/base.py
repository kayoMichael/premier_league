from http.client import HTTPException
from xml.etree import ElementTree
import hashlib
import asyncio
import aiohttp
from functools import partial
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from datetime import datetime
import requests
import re
from dataclasses import dataclass, field
from requests import Response
from bs4 import BeautifulSoup
from lxml import etree
from typing import Optional

from premier_league.utils.methods import clean_xml_text


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
    """

    url: str
    requires_season: bool = True
    page: ElementTree = field(default_factory=lambda: None, init=False)
    season: str = field(default=None, init=False)
    target_season: str = field(default=None)

    def __post_init__(self):
        """
        Initialize the current and previous seasons based on the current date or target season.

        Raises:
            ValueError: If the target_season is invalid or in an incorrect format.
        """
        if self.requires_season:
            return

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
            elif int(self.target_season[:4]) < 1992:
                raise ValueError(
                    "Invalid target_season. The First Premier League season was 1992-1993. It cannot be before 1992."
                )
            if self.url[-1] != "/":
                self.season = f"{self.target_season[:4]}-{self.target_season[7:]}"
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
            response: Response = requests.get(
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

    @staticmethod
    def convert_to_xml(bsoup: BeautifulSoup):
        """
        Convert a BeautifulSoup object to an lxml ElementTree.

        Args:
            bsoup (BeautifulSoup): The BeautifulSoup object to convert.

        Returns:
            ElementTree: The converted XML tree.
        """
        return etree.HTML(str(bsoup))

    @staticmethod
    def additional_scrapper(additional_url):
        """
        Create a new BaseScrapper instance for an additional URL without creating a new object.

        Args:
            additional_url (str): The URL to scrape.

        Returns:
            BaseScrapper: A new BaseScrapper instance with the page loaded.
        """
        scrapper = BaseScrapper(url=additional_url)
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

    def get_cache_path(self, url):
        filename = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{filename}.txt"

    async def fetch_page(self, session, url, pbar, rate_limit):
        cache_path = self.get_cache_path(url)
        if cache_path.exists():
            pbar.update(1)
            return etree.HTML(cache_path.read_text(encoding="utf-8"))

        try:
            await asyncio.sleep(rate_limit)
            async with session.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 "
                        "Safari/537.36"
                    ),
                },
            ) as response:
                html = await response.text()
                cache_path.write_text(html, encoding="utf-8")

                pbar.update(1)
                return etree.HTML(html)

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_all(self, urls, max_concurrent=15, rate_limit=1):
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(
                self._scrape_all(urls, max_concurrent, rate_limit)
            )
        except RuntimeError:
            return asyncio.run(self._scrape_all(urls, max_concurrent, rate_limit))

    async def _scrape_all(self, urls, max_concurrent, rate_limit):
        async with aiohttp.ClientSession() as session:
            with tqdm(total=len(urls), desc="Scraping Progress") as pbar:
                semaphore = asyncio.Semaphore(max_concurrent)

                async def bounded_fetch(url):
                    async with semaphore:
                        return await self.fetch_page(session, url, pbar, rate_limit)

                tasks = [bounded_fetch(url) for url in urls]
                results = await asyncio.gather(*tasks)

                return [r for r in results if r is not None]

    def _get_list_by_xpath(
        self, page: ElementTree, xpath: str, clean: Optional[bool] = True
    ) -> Optional[list]:
        """
        Get a list of elements matching the given XPath.

        Args:
            xpath (str): The XPath query to execute.
            clean (bool, optional): Whether to clean the text content of the elements. Defaults to True.

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

    def process_xpath(self, xpath: str, clean: Optional[bool] = True) -> Optional[list]:
        """
        Get a list of elements matching the given XPath using a ThreadPoolExecutor.

        Args:
            xpath (str): The XPath query to execute.
            clean (bool, optional): Whether to clean the text content of the elements. Defaults to True.

        Returns:
            Optional[list]: A list of matching elements, or an empty list if no matches are found.
        """
        with ThreadPoolExecutor() as executor:
            func = partial(self._get_list_by_xpath, xpath=xpath, clean=clean)
            results = list(executor.map(func, self.pages))

        return [item for sublist in results for item in sublist]
