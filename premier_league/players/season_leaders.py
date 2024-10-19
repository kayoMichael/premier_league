from premier_league.base import BaseScrapper
from typing import Literal
from ..utils.xpath import PLAYERS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import json
import csv
import re


class PlayerSeasonLeaders(BaseScrapper):
    def __init__(self, stat_type: Literal['G', 'A'],  target_season: str = None):
        self.stat_type = stat_type
        self.stat_url = self._get_url()
        super().__init__(self.stat_url, target_season)
        self.page = self.request_url_page()
        self.season_top_players_list = self._init_top_stats_table()

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
                sublist[2:4] = [f"{sublist[2]}, {sublist[3]}"]
                i += (parition + 1)
            else:
                i += parition
            partitioned.append(sublist)
        return partitioned[:21]

    def get_top_stats_list(self) -> list:
        return self.season_top_players_list

    def get_top_stats_csv(self, file_name):
        with open(f'{file_name}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.season_top_players_list)

    def get_top_stats_json(self, file_name):
        json_data = []
        headers = self.season_top_players_list[0]
        for row in self.season_top_players_list[1:]:
            json_data.append(dict(zip(headers, row)))

        with open(f'{file_name}.json', 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=2)

    def get_top_stats_pdf(self, file_name):
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdf = canvas.Canvas(f"{file_name}.pdf", pagesize=A3)

        pdf.setFont("Arial", 16)
        main_words = "Goal Scorer" if self.stat_type == "G" else "Assist Leader"
        title = f"{self.season} Premier League Top {main_words}"
        title_width = pdf.stringWidth(title, "Arial", 16)
        pdf.drawString((A3[0] - title_width) / 2 + 0.5, A3[1] - 30 + 0.1, title)
        pdf.drawString((A3[0] - title_width) / 2, A3[1] - 30, title)

        pdf.setFont("Arial", 12)
        table = Table(self.season_top_players_list)

        table_styles = [('BACKGROUND', (0, 0), (-1, 0), HexColor("#cccccc")),
                        ('BACKGROUND', (0, 1), (-1, 1), HexColor("#FFD700")),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                        ('FONTSIZE', (0, 0), (-1, -1), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('TOPPADDING', (0, 0), (-1, -1), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]
        table.setStyle(TableStyle(table_styles))
        table.wrapOn(pdf, 0, 0)
        table_width, table_height = table.wrapOn(pdf, A3[0] - 2 * inch, A3[1] - 2 * inch)
        x = (A3[0] - table_width) / 2
        y = A3[1] - table_height - 1 * inch
        table.drawOn(pdf, x, y)

        pdf.save()
