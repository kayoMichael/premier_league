from premier_league.base import BaseDataSetScrapper
from premier_league.utils.url import MatchUrl, MATCH_STATISTICS_LEAGUE
from premier_league.utils.methods import current_season
from premier_league.utils.xpath import MATCHES, XPathElement

from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import json, time

OUT = Path("matches")
OUT.mkdir(exist_ok=True)

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

    @staticmethod
    def extract_all_url(root: XPathElement, url: str):
        script = root.xpath(MATCHES.MATCH_URLS)[0]

        data = json.loads(script)

        fixtures = data["props"]["pageProps"]["fixtures"]["allMatches"]
        matches = [(int(m["id"]), m["pageUrl"]) for m in fixtures]
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            for mid, pageUrl in matches:
                out_file = OUT / f"{mid}.json"
                if out_file.exists():
                    continue

                try:
                    with page.expect_response(lambda r, mid=mid: "matchDetails" in r.url and f"matchId={mid}" in r.url
                                                                 and r.status == 200,
                                              timeout=20000) as resp_info:
                        page.goto(f"https://www.fotmob.com{pageUrl}",
                                  wait_until="domcontentloaded")

                    data = resp_info.value.json()
                    got_id = str(data.get("general", {}).get("matchId"))
                    if data.get("error") or got_id != str(mid):
                        print(f"bad payload for {mid}: {data.get('message')}")

                    out_file.write_text(json.dumps(data, indent=2))
                    print(f"saved {mid}: {data['general']['matchName']}")
                    time.sleep(4)
                except PWTimeout:
                    print(f"timeout on {mid}, skipping")
                    continue

if __name__ == '__main__':
    scraper = MatchPipeline()
    scraper.process_data()