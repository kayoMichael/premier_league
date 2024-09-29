from http.client import HTTPException
from xml.etree import ElementTree

import requests
from dataclasses import dataclass, field
from requests import Response
from bs4 import BeautifulSoup
from lxml import etree


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






