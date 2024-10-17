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
                raise ValueError("Invalid format for target_season. Please use 'YYYY-YY' (e.g., '2024-25').")
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
        self.find_european_competition_spot()
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdf = canvas.Canvas(f"{file_name}.pdf", pagesize=A3)
        pdf.setFont("Arial", 12)
        table = Table(self.ranking_list)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), HexColor("#f2f2f2")),
                                  ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                  ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                  ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                                  ('FONTSIZE', (0, 0), (-1, -1), 12),
                                  ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                                  ('TOPPADDING', (0, 0), (-1, -1), 12),
                                  ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        table.wrapOn(pdf, 0, 0)
        table_width, table_height = table.wrapOn(pdf, A3[0] - 2 * inch, A3[1] - 2 * inch)
        x = (A3[0] - table_width) / 2
        y = A3[1] - table_height - inch
        table.drawOn(pdf, x, y)

        pdf.save()

    def find_european_competition_spot(self) -> dict:
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
        cl_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.prev_season}_UEFA_Champions_League")
        cl_winner = self.find_tournament_winner(cl_page, RANKING.UEFA_WINNER)

        # Previous Europa League Winner (Potential Champions League Spot)
        europa_winner = None
        if int(self.prev_season[:4]) >= 2009:
            europa_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.prev_season}_UEFA_Europa_League")
            europa_winner = self.find_tournament_winner(europa_page, RANKING.UEFA_WINNER)

        # Previous Europa Conference League Winner (Potential Europa League Spot)
        conference_winner = None
        if int(self.prev_season[:4]) >= 2021:
            conference_page = self.additional_scrapper(f"https://en.wikipedia.org/wiki/{self.prev_season}_UEFA_Europa_Conference_League")
            conference_winner = self.find_tournament_winner(conference_page, RANKING.UEFA_WINNER)

        return {f"{self.season} EFL Cup Winner": efl_winner, f"{self.season} FA Cup Winner": fa_winner,
                f"{self.prev_season} Champions League Winner": cl_winner,
                f" {self.prev_season} Europa Winner": europa_winner,
                "{prev_seaoson} Conference League Winner": conference_winner}

    @staticmethod
    def find_tournament_winner(cup_page, xpath: str) -> str:
        result = cup_page.get_list_by_xpath(xpath)
        return result[0] if result else None

    @staticmethod
    def additional_scrapper(additional_url) -> BaseScrapper:
        scrapper = BaseScrapper(url=additional_url)
        scrapper.page = BaseScrapper.request_url_page(scrapper)
        return scrapper

