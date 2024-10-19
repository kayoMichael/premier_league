from premier_league.base import BaseScrapper
from typing import Literal
from ..utils.xpath import PLAYERS
import pdb
import re


class PlayerSeasonLeaders(BaseScrapper):
    def __init__(self, stat_type: Literal['G', 'A'],  target_season: str = None):
        self.stat_type = stat_type
        self.stat_url = self._get_url()
        super().__init__(self.stat_url, target_season)
        self.page = self.request_url_page()
        self.season_top_players = self._init_top_stats_table()

    def _get_url(self):
        if self.stat_type == "G":
            return "https://www.worldfootball.net/scorer/eng-premier-league-{SEASON}/"
        else:
            return "https://www.worldfootball.net/assists/eng-premier-league-{SEASON}/"

    def _init_top_stats_table(self) -> list[list[str]]:
        player_list = self.get_list_by_xpath(PLAYERS.PLAYER_SCORING)
        top_players = [item for item in player_list if not re.match(r'^\d+\.$', item) and
                       not re.match(r'^\d{4}/\d{4}$', item) and
                       item.strip() and
                       item != "\n" and
                       item != 'Latest news »']

        partitioned = [["Name", "Country", "Club", "Goals", "In Play Goals+Penalty"]] if self.stat_type == "G" else \
            [["Name", "Country", "Club", "Assists"]]
        i = 0
        parition = 4 if self.stat_type == "A" else 5
        while i < len(top_players):
            sublist = top_players[i:i + parition]
            if len(sublist) > 3 and not sublist[3].isdigit():
                sublist = top_players[i:i + parition + 1]
                i += (parition + 1)
            else:
                i += parition
            partitioned.append(sublist)
        return partitioned

    def get_top_scorers_list(self) -> list:
        return self.season_top_players


