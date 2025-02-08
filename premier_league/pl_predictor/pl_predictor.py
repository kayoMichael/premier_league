from premier_league.base import BaseDataSetScrapper
from ..utils.url import PredictorURL
from ..utils.xpath import MATCHES
from datetime import datetime


class PLPredictor(BaseDataSetScrapper):
    def __init__(self):
        super().__init__()
        self.current_season = None
        self.urls = []
        self.used_table_index = [2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]

    def initialize_data_set(self):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        if current_month >= 8:
            self.current_season = f"{current_year}-{current_year + 1}"
        else:
            self.current_season = f"{current_year - 1}-{current_year}"

        for i in range(2018, int(self.current_season.split("-")[1])):
            urlist = PredictorURL.get_all(f"{i}-{i+1}")
            self.urls.extend(urlist)
        self.pages = self.scrape_all(self.urls, max_concurrent=1, rate_limit=4, desc="Fetching Season Schedule")
        relevant_urls = self.process_xpath(MATCHES.MATCH_REPORT_URL, add_str="https://fbref.com", desc="Processing Match URLs")
        # Fetch Game Details
        self.scrape_all(relevant_urls, max_concurrent=1, rate_limit=4, desc="Fetching Match Details")
        game_data_table = self.process_xpath(MATCHES.GAME_TABLE, clean=False, desc="Processing Match Data")
