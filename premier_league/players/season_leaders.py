import os
import re
import traceback
from typing import Literal, Optional

from premier_league.base import BaseScrapper

from ..utils.methods import export_to_csv, export_to_json, require_dependency
from ..utils.url import PLAYERS_URL
from ..utils.xpath import PLAYERS


class PlayerSeasonLeaders(BaseScrapper):
    """
    A class to scrape and process top player statistics (goals or assists) for a season in Top 5 European League.

    This class inherits from BaseScrapper and provides methods to retrieve, process, and export
    player statistics in various formats (list, CSV, JSON, PDF).

    Attributes:
        stat_type (Literal['G', 'A']): The type of statistic to scrape ('G' for goals, 'A' for assists).
        stat_url (str): The URL to scrape data from.
        page: The scraped web page content.
        _season_top_players_list (list): Processed list of top players and their statistics.
    """

    def __init__(
        self,
        stat_type: Literal["G", "A"],
        target_season: Optional[str] = None,
        league: Optional[str] = "Premier League",
        cache: Optional[bool] = True,
    ):
        """
        Initialize the PlayerSeasonLeaders object.

        Args:
            stat_type (Literal['G', 'A']): The type of statistic to scrape ('G' for goals, 'A' for assists).
            target_season (str, optional): The specific season to scrape data for. Defaults to None.
            league (str, optional): The league to scrape data for. Defaults to "Premier League".
        """
        self.league = league
        self.stat_type = stat_type
        self.stat_url = self._get_url()
        self.season_limit = self.find_season_limit()
        super().__init__(
            url=self.stat_url,
            target_season=target_season,
            season_limit=self.season_limit,
            cache=cache,
        )
        self.page = self.request_url_page()
        self._season_top_players_list = self._init_top_stats_table()

    def _get_url(self) -> str:
        """
        Generate the URL for scraping based on the stat_type.

        Returns:
            str: The URL to scrape data from.
        """
        return PLAYERS_URL.get(self.league.lower(), self.stat_type)

    def _init_top_stats_table(self) -> list[list[str]]:
        """
        Initialize and process the top statistics table.

        This method scrapes the raw data, cleans it, and structures it into a list of lists.

        Returns:
            list[list[str]]: Processed list of top players and their statistics.
        """
        player_list = self.get_list_by_xpath(PLAYERS.PLAYER_STATS)
        top_players = [
            item
            for item in player_list
            if not re.match(r"^\d+\.$", item)
            and not re.match(r"^\d{4}/\d{4}$", item)
            and item.strip()
            and item != "\n"
            and item != "Latest news »"
        ]

        partitioned = (
            [["Name", "Country", "Club", "Goals", "In Play Goals+Penalty"]]
            if self.stat_type == "G"
            else [["Name", "Country", "Club", "Assists"]]
        )

        i = 0
        partition = 4 if self.stat_type == "A" else 5
        while i < len(top_players):
            sublist = top_players[i : i + partition]
            if len(sublist) > 3 and not sublist[3].isdigit():
                sublist = top_players[i : i + partition + 1]
                sublist[2:4] = [f"{sublist[2]}, {sublist[3]}"]
                i += partition + 1
            else:
                i += partition
            partitioned.append(sublist)
        return partitioned

    def find_season_limit(self):
        """
        Find the season limit for the given league.

        Returns:
            int: The season limit for the given league.
        """
        if self.stat_type == "G" and self.league.lower() == "premier league":
            return 1995

        season_limit_map = {
            "premier league": 1997,
            "la liga": 2008,
            "serie a": 2010,
            "ligue 1": 2010,
            "bundesliga": 1988,
        }
        return season_limit_map[self.league.lower()]

    def get_top_stats_list(self, limit: int = None) -> list:
        """
        Get the processed list of top players and their statistics.

        Args:
            limit (int, optional): The number of top players to include. Defaults to None.
        Returns:
            list: The season_top_players_list attribute.
        """
        return self._season_top_players_list[: limit + 1 if limit else 100]

    def get_top_stats_csv(self, file_name: str, header: str = None, limit: int = None):
        """
        Export the top statistics to a CSV file.

        Args:
            file_name (str): The name of the file to save (without extension).
            header    (str, optional): The header for the CSV file. Defaults to None.
            limit     (int, optional): The number of top players to include. Defaults to None.
        """

        export_to_csv(file_name, self.get_top_stats_list(limit), header)

    def get_top_stats_json(self, file_name: str, header: str = None, limit: int = None):
        """
        Export the top statistics to a JSON file.

        Args:
            file_name (str): The name of the file to save (without extension).
            header    (str, optional): The header for the JSON file. Defaults to None.
            limit     (int, optional): The number of top players to include. Defaults to None.
        """
        export_to_json(file_name, self.get_top_stats_list(limit), header_1=header)

    def get_top_stats_pdf(self, file_name: str, path: str):
        """
        Export the top 20 player statistics to a PDF file. Requires premier_league[pdf] to be installed.

        This method creates a formatted PDF with a title, table of statistics,
        and applies styling to enhance readability.

        Args:
            file_name (str): The name of the file to save (without extension).
            path (str): The path to save the PDF file
        """
        require_dependency("reportlab", "pdf")
        from reportlab.lib import colors
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A3
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.platypus import Table, TableStyle

        os.makedirs(path, exist_ok=True)
        pdf = canvas.Canvas(f"{path}/{file_name}.pdf", pagesize=A3)

        # Set up the title
        try:
            pdf.setFont("Helvetica", 16)
            main_words = "Goal Scorer" if self.stat_type == "G" else "Assist Leader"
            title = f"{self.season} Premier League Top {main_words}"
            title_width = pdf.stringWidth(title, "Helvetica", 16)
            pdf.drawString((A3[0] - title_width) / 2 + 0.5, A3[1] - 30 + 0.1, title)
            pdf.drawString((A3[0] - title_width) / 2, A3[1] - 30, title)

            # Create and style the table
            pdf.setFont("Helvetica", 12)
            table = Table(self._season_top_players_list[:22])

            table_styles = [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#cccccc")),
                ("BACKGROUND", (0, 1), (-1, 1), HexColor("#FFD700")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
            table.setStyle(TableStyle(table_styles))

            # Position and draw the table
            table_width, table_height = table.wrapOn(
                pdf, A3[0] - 2 * inch, A3[1] - 2 * inch
            )
            x = (A3[0] - table_width) / 2
            y = A3[1] - table_height - 1 * inch
            table.drawOn(pdf, x, y)

            pdf.save()
        except Exception:
            if os.path.exists(path) and not os.listdir(path):
                os.rmdir(path)
            traceback.print_exc()
            raise Exception
