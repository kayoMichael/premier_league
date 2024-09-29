from premier_league.base import PremierLeague

from ..utils.methods import remove_duplicates
from ..utils.xpath import RANKING


class RankingTable(PremierLeague):
    def __init__(self):
        super().__init__("https://www.premierleague.com/tables")
        self.soup = self.parse_to_html()
        self.page = self.request_url_page()
        self.ranking_list = self.init_ranking_table()

    def init_ranking_table(self) -> list:
        ranking_headers = remove_duplicates(self.get_list_by_xpath(RANKING.HEADERS))
        ranking_rows = self.get_list_by_xpath(RANKING.ROWS)
        ranking_headers.insert(1, "Club")
        ranking_headers.insert(2, "ID")
        ranking_list = [ranking_headers] + [[index] + ranking_rows[i: i + 10] for index, i in enumerate(range(0, len(ranking_rows), 10), start=1)]
        return ranking_list

    def get_prem_ranking_list(self):
        return self.ranking_list
