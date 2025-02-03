from premier_league.base import BaseDataSetScrapper
from ..utils.url import PredictorURL
from ..utils.xpath import MATCHES
from datetime import datetime


class PLPredictor(BaseDataSetScrapper):
    def __init__(self):
        super().__init__()
        self.current_season = None
        self.urls = []

    def initialize_data_set(self):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        if current_month >= 8:
            self.current_season = f"{current_year}-{current_year + 1}"
        else:
            self.current_season = f"{current_year - 1}-{current_year}"

        for i in range(2018, int(self.current_season.split("-")[1])):
            url = PredictorURL.BASE_URLS["PREM"].format(SEASON=f"{i}-{i+1}")
            self.urls.append(url)

        self.pages = self.scrape_all(self.urls, max_concurrent=min(len(self.urls), 10))
        relevant_urls = self.process_xpath(MATCHES.MATCH_REPORT_URL, self.pages)
