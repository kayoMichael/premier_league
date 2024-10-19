import pdb

from premier_league.base import BaseScrapper
import csv
from datetime import datetime
import json
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from ..utils.methods import remove_qualification_and_relegation
from ..utils.xpath import RANKING


class RankingTable(BaseScrapper):
    def __init__(self, target_season: str = None):
        self.season = None
        self.prev_season = None
        self.target_season = target_season
        self.current_date = datetime.now()
        self.initialize_season()
        super().__init__(f"https://en.wikipedia.org/wiki/{self.season}_Premier_League")
        self.page = self.request_url_page()
        self.ranking_list = self.init_ranking_table()

    def init_ranking_table(self) -> list:
        ranking_rows = remove_qualification_and_relegation(self.get_list_by_xpath(RANKING.CURRENT_RANKING))
        ranking_list = [ranking_rows[i: i + 10] for i in range(0, len(ranking_rows), 10)]
        return ranking_list

    def get_prem_ranking_list(self) -> list:
        return self.ranking_list

    def initialize_season(self) -> None:
        if not self.target_season:
            current_year = self.current_date.year
            current_month = self.current_date.month
            if current_month >= 8:
                self.season = f"{current_year}-{str(current_year + 1)[2:]}"
                self.prev_season = f"{current_year - 1}-{str(current_year)[2:]}"
            else:
                self.season = f"{current_year - 1}-{str(current_year)[2:]}"
                self.prev_season = f"{current_year - 2}-{str(current_year - 1)[2:]}"
        else:
            if not re.match(r'^\d{4}-\d{2}$', self.target_season):
                raise ValueError("Invalid format for target_season. Please use 'YYYY-YY' (e.g., '2024-25') with a regular hyphen.")
            elif int(self.target_season[:4]) > self.current_date.year:
                raise ValueError("Invalid target_season. It cannot be in the future.")
            elif int(self.target_season[:4]) < 1992:
                raise ValueError("Invalid target_season. The First Premier League season was 1992-93. It cannot be before 1992.")
            self.season = self.target_season
            self.prev_season = f"{int(self.season[:4]) - 1}-{str(int(self.season[:4]))[2:]}"

    def get_prem_ranking_csv(self, file_name: str) -> None:
        with open(f'{file_name}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.ranking_list)

    def get_prem_ranking_json(self, file_name: str) -> None:
        json_data = []
        headers = self.ranking_list[0]
        for row in self.ranking_list[1:]:
            json_data.append(dict(zip(headers, row)))

        with open(f'{file_name}.json', 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=2)

    def get_prem_ranking_pdf(self, file_name: str) -> None:
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdf = canvas.Canvas(f"{file_name}.pdf", pagesize=A3)

        pdf.setFont("Arial", 16)
        title = f"Premier League Table {self.season}"
        title_width = pdf.stringWidth(title, "Arial", 16)

        pdf.drawString((A3[0] - title_width) / 2 + 0.5, A3[1] - 30 + 0.1, title)
        pdf.drawString((A3[0] - title_width) / 2, A3[1] - 30, title)

        pdf.setFont("Arial", 12)
        table = Table(self.ranking_list)

        if int(self.season[:4]) > 2019:
            european_spots = self.find_european_qualification_spot()
        else:
            european_spots = self.scrap_european_qualification_spot()

        static_table_styles = [('BACKGROUND', (0, 0), (-1, 0), HexColor("#cccccc")),
                               ('BACKGROUND', (0, 1), (-1, 4), HexColor("#aaff88")),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                               ('FONTSIZE', (0, 0), (-1, -1), 12),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                               ('TOPPADDING', (0, 0), (-1, -1), 12),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black),
                               ('BACKGROUND', (0, -3), (-1, -1), HexColor("#e06666"))]

        all_styles = static_table_styles + european_spots
        pdb.set_trace()
        table.setStyle(TableStyle(all_styles))
        table.wrapOn(pdf, 0, 0)
        table_width, table_height = table.wrapOn(pdf, A3[0] - 2 * inch, A3[1] - 2 * inch)
        x = (A3[0] - table_width) / 2
        y = A3[1] - table_height - 1 * inch
        table.drawOn(pdf, x, y)

        pdf.save()

    def find_european_qualification_spot(self) -> list[tuple[str, tuple[int, int], tuple[int, int]] | list]:
        m_conference = None
        m_europa = []
        m_champions = []
        all_current_teams = [self.ranking_list[index][1] for index in range(1, len(self.ranking_list))]
        if self.target_season is not None:
            domestic_and_european_winners = self._find_european_competition_spot()
            for index, team in enumerate(all_current_teams, start=1):
                for tournament, winner in domestic_and_european_winners.items():
                    if tournament == "EFL" and winner == team:
                        m_conference = index
                    elif tournament == "FA" and winner == team:
                        m_europa.append(index)
                    elif tournament == "CL" and winner == team:
                        m_champions.append(index)
                    elif tournament == "UEL" and winner == team:
                        m_champions.append(index)
                    elif tournament == "UECL" and winner == team:
                        m_europa.append(index)

        cl_european_spots = all_current_teams[:4]
        uel_style = []
        cl_style = []
        uecl_style = []

        europa_counter = 2
        conference_counter = 1

        # Determine if Europa League Qualifying Team already qualified to a higher Tournament (Champions League)
        for index in m_europa:
            if all_current_teams[index] not in cl_european_spots:
                uel_style.append(('BACKGROUND', (0, index), (-1, index), HexColor("#99cc00")))
                europa_counter -= 1

        # Determine if Team already qualified to Champions League by League Position.
        for index in m_champions:
            if all_current_teams[index] not in cl_european_spots:
                cl_style.append(('BACKGROUND', (0, index), (-1, index), HexColor("#aaff88")))

        # Determine if Conference League Qualifying Team already qualified to a higher Tournament
        if m_conference is not None:
            champions_matches = self.is_team_in_european_competition(m_conference, m_champions, all_current_teams)
            europa_matches = self.is_team_in_european_competition(m_conference, m_europa, all_current_teams)
            if not champions_matches and not europa_matches and all_current_teams[m_conference] not in cl_european_spots:
                uecl_style = ('BACKGROUND', (0, m_conference), (-1, m_conference), HexColor("#6aa84f"))
                conference_counter -= 1

        # Determine if sixth place will receive Europa, Champions League or Europa Conference League spot
        index = 5
        while europa_counter > 0:
            if index in m_champions:
                index += 1
            if index in m_europa:
                index += 1
            else:
                uel_style.append(('BACKGROUND', (0, index), (-1, index), HexColor("#99cc00")))
                europa_counter -= 1
                index += 1

        if conference_counter == 1:
            uecl_style = ('BACKGROUND', (0, index), (-1, index), HexColor("#6aa84f"))
        return [uecl_style] + uel_style + cl_style

    def _find_european_competition_spot(self) -> dict:
        # FA Cup Winner for this Season (Potential Europa League Spot)
        fa_cup_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.season}_FA_Cup")
        fa_winner = self.find_tournament_winner(fa_cup_page, RANKING.CUP_WINNER)

        # EFL Cup Winner for this Season (Potential Europa Conference League Spot)
        cup_name = "EFL_Cup"
        if int(self.season[:4]) <= 2015:
            cup_name = "Football_League_Cup"
        efl_cup_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.season}_{cup_name}")
        efl_winner = self.find_tournament_winner(efl_cup_page, RANKING.CUP_WINNER)

        # Previous Champions League Winner (Potential Champions League Spot)
        cl_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.season}_UEFA_Champions_League")
        cl_winner = self.find_tournament_winner(cl_page, RANKING.UEFA_WINNER)

        # Previous Europa League Winner (Potential Champions League Spot)
        europa_winner = None
        if int(self.prev_season[:4]) >= 2009:
            europa_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.season}_UEFA_Europa_League")
            europa_winner = self.find_tournament_winner(europa_page, RANKING.UEFA_WINNER)

        # Previous Europa Conference League Winner (Potential Europa League Spot)
        conference_winner = None
        if int(self.prev_season[:4]) >= 2021:
            conference_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.season}_UEFA_Europa_Conference_League")
            conference_winner = self.find_tournament_winner(conference_page, RANKING.UEFA_WINNER)

        return {"EFL": efl_winner,
                "FA": fa_winner,
                "CL": cl_winner,
                "UEL": europa_winner,
                "UECL": conference_winner}

    def scrap_european_qualification_spot(self) -> list:
        pass

    @staticmethod
    def is_team_in_european_competition(team_index, competition_indices, all_teams):
        return [i for i in competition_indices if all_teams[team_index] == all_teams[i]]

    @staticmethod
    def find_tournament_winner(cup_page, xpath: str) -> str:
        result = cup_page.get_list_by_xpath(xpath)
        return result[0] if result else None

    @staticmethod
    def additional_scrapper(additional_url) -> BaseScrapper:
        scrapper = BaseScrapper(url=additional_url)
        scrapper.page = BaseScrapper.request_url_page(scrapper)
        return scrapper

