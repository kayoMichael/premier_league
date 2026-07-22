from premier_league.base import BaseDataSetScrapper
from premier_league.utils.url import MatchUrl, MATCH_STATISTICS_LEAGUE
from premier_league.utils.methods import current_season
from premier_league.utils.xpath import MATCHES, XPathElement

import json

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
                    league=league,
                    page_type="fixtures",
                )

                urls.append(f"{url}?season={season}&page=9999&group=by-date")

        self.scrape_and_process_all(urls, rate_limit=4, return_html=False, process_func=self.extract_all_url)

        urls = []
        for league in MATCH_STATISTICS_LEAGUE:
            for year in range(2016, curr_season + 1):
                season = str(year) if league == "mls" else f"{year}-{year + 1}"
                urls.extend([f"{MatchUrl.get(
                    league=league,
                    page_type="overview"
                )}?season={season}", f"{MatchUrl.get(
                    league=league,
                    page_type="stats"
                )}/players?season={season}", f"{MatchUrl.get(
                    league=league,
                    page_type="overview"
                )}/teams?season={season}"])

        self.scrape_and_process_all(urls, rate_limit=4, return_html=False)

    def extract_all_url(self, root: XPathElement, url: str):
        script = root.xpath(MATCHES.MATCH_URLS)[0]

        data = json.loads(script)

        fixtures = data["props"]["pageProps"]["fixtures"]
        urls = ["https://www.fotmob.com" + match["pageUrl"] for match in fixtures["allMatches"]]

        result = self.scrape_and_process_all(urls, rate_limit=4, return_html=False)

if __name__ == '__main__':
    scraper = MatchPipeline()
    scraper.process_data()