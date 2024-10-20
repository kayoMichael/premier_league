from premier_league.base import BaseScrapper
from premier_league.utils.xpath import PLAYERS
from premier_league.utils.methods import clean_xml_text

from prettytable import PrettyTable


class Transfers(BaseScrapper):
    def __init__(self, target_season: str = None):
        super().__init__("https://www.worldfootball.net/transfers/eng-premier-league-{SEASON}/", target_season)
        self.page = self.request_url_page()
        self.season_top_players = self._init_transfers_table()

    def _init_transfers_table(self) -> dict[str, list[str]]:
        transfer_list = self.get_list_by_xpath(PLAYERS.TRANSFERS, False)

        team_transfer_dict = {}
        for transfer in transfer_list:
            try:
                target_team = transfer.xpath('.//div[@class="head"]/h2/text()')[0]
                player_transfers = [clean_xml_text(e) for e in
                                    transfer.xpath('.//div[@class="data"]//table//tr//text()') if clean_xml_text(e)]
                team_transfer_dict[target_team.split(" » ")[0].strip()] = player_transfers
            except IndexError:
                break
        return team_transfer_dict

    def print_transfer_table(self, team: str):
        in_table = PrettyTable()
        out_table = PrettyTable()
        field_names = ["Date", "Name", "Position", "Club"]
        in_table.field_names = field_names
        out_table.field_names = field_names

        data = self.season_top_players[team]
        index = 1
        current_type = 'In'
        while index < len(data):
            target_data = data[index: index + 4]
            if "Out" in target_data:
                current_type = 'Out'
                target_data = target_data[1:] + [data[index + 4]]
                index += 5
            else:
                index += 4
            date, name, position, club = target_data
            if current_type == 'In':
                in_table.add_row([date, name, position, club])
            elif current_type == 'Out':
                out_table.add_row([date, name, position, club])

        print(f"{team} >> Transfers {self.season} In:")
        print(in_table)
        print(f"\n{team} >> Transfers {self.season} Out:")
        print(out_table)