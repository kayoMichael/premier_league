import pdb

from base import PremierLeague


class RankingTable(PremierLeague):
    def __init__(self):
        super().__init__("https://www.premierleague.com/tables")
        pdb.set_trace()
        self.soup = self.parse_to_html()
        self.thead = self.soup.find('thead')
        self.rows = self.thead.find_all('tr')
        self.header_list = []
        self.headers = self.rows[0].find_all('th')
        self.tbody = self.soup.find('tbody')
        self.rows = self.tbody.find_all('tr')
        self.data = []

    def get_prem_ranking(self):
        for header in self.headers:
            first_div = header.find('div')
            if first_div:
                self.header_list.append(first_div.get_text(strip=True))
            else:
                self.header_list.append(header.get_text(strip=True))

        self.header_list.pop()
        self.data.append(self.header_list)

        for row in self.rows:
            try:
                cols = row.find_all('td')
                position = cols[0].find('span').get_text(strip=True)
                club = cols[1].find('span', class_="league-table__team-name--long").get_text(strip=True)
                played = cols[2].get_text(strip=True)
                won = cols[3].get_text(strip=True)
                drawn = cols[4].get_text(strip=True)
                lost = cols[5].get_text(strip=True)
                gf = cols[6].get_text(strip=True)
                ga = cols[7].get_text(strip=True)
                gd = cols[8].get_text(strip=True)
                points = cols[9].get_text(strip=True)
                fixtures = cols[10].find_all("span", class_="match-fixture__team-name")
                next_5_games = [fixture.find("abbr").get("title") for fixture in fixtures if
                                fixture.find("abbr").get("title") != club]
                next_game = cols[11].find("span").find("abbr").get("title")

                cols_data = [position, club, played, won, drawn, lost, gf, ga, gd, points, next_5_games, next_game]

                self.data.append(cols_data)
            except Exception:
                continue
        return self.data