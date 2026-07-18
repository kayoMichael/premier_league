from premier_league.base import BaseDataSetScrapper
from premier_league.utils.url import MatchUrl, MATCH_STATISTICS_LEAGUE
from premier_league.utils.methods import current_season

class MatchPipeline(BaseDataSetScrapper):
    def __init__(self):
        super().__init__()

    def process_data(self):
        urls = []
        curr_season = current_season()
        for league in MATCH_STATISTICS_LEAGUE:
            for year in range(2016, curr_season + 1):
                season = str(year) if league == "mls" else f"{year}-{year + 1}"

                url = MatchUrl.get(
                    season,
                    league=league,
                    page_type="fixtures",
                )

                urls.append(f"{url}&page=9999&group=by-date")

        result = self.scrape_and_process_all(urls, rate_limit=4)


    def extract_all_url(self, page: str, url: str):
        pass


if __name__ == '__main__':
    scraper = MatchPipeline()
    scraper.process_data()