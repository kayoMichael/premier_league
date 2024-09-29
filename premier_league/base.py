from http.client import HTTPException
from xml.etree import ElementTree

import requests
from dataclasses import dataclass, field
from requests import Response
from bs4 import BeautifulSoup
from lxml import etree
from typing import Optional

from premier_league.utils.methods import clean_xml_text


@dataclass
class PremierLeague:
    url: str
    page: ElementTree = field(default_factory=lambda: None, init=False)

    def make_request(self) -> Response:
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
        response: Response = self.make_request()
        return BeautifulSoup(markup=response.content, features="html.parser")

    @staticmethod
    def convert_to_xml(bsoup: BeautifulSoup):
        return etree.HTML(str(bsoup))

    def request_url_page(self) -> ElementTree:
        bsoup: BeautifulSoup = self.parse_to_html()
        return self.convert_to_xml(bsoup=bsoup)

    def get_list_by_xpath(self, xpath: str, remove_empty: Optional[bool] = True) -> Optional[list]:
        elements: list = self.page.xpath(xpath)
        if remove_empty:
            elements_valid: list = [clean_xml_text(e) for e in elements if clean_xml_text(e)]
        else:
            elements_valid: list = [clean_xml_text(e) for e in elements]
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