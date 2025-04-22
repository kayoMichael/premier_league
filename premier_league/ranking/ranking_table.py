import os
import re
import traceback
from typing import Optional, Union

from premier_league.base import BaseScrapper

from ..utils.methods import (
    export_to_csv,
    export_to_dict,
    export_to_json,
    remove_qualification_relegation_and_css,
    require_dependency,
)
from ..utils.url import RANKING_URL
from ..utils.xpath import RANKING


class RankingTable(BaseScrapper):
    """
    A class to scrape and process ranking data for the Top 5 Leagues.

    This class inherits from BaseScrapper and provides methods to retrieve,
    process, and output ranking data for the Top 5 European Leagues in various formats.

    Attributes:
        season (str): The current season.
        target_season (str): The specific season to scrape data for, if provided.
        page: The scraped web page containing the ranking data.
        ranking_list (list): The processed ranking data.
    """

    def __init__(
        self,
        league: Optional[str] = "Premier League",
        target_season: Optional[str] = None,
        cache: Optional[bool] = True,
    ):
        """
        Initialize the RankingTable instance.

        Args:
            target_season (str, optional): The specific season to scrape data for.
                                           If not provided, the current season is used.
            league (str, optional): The league to scrape data for. Defaults to "Premier League".
        """
        self.league = league.title() if league else "Premier League"
        super().__init__(
            RANKING_URL.get(league=self.league.lower(), target_season=target_season),
            target_season=target_season,
            season_limit=self.find_season_limit(),
            cache=cache,
        )
        self.page = self.request_url_page()
        self.ranking_list = self._init_ranking_table()
        self.cache = cache

    def _init_ranking_table(self) -> list:
        """
        Initialize the ranking table by scraping and processing the data.

        Returns:
            list: A list of lists containing the processed ranking data.
        """
        teams = list(
            filter(
                lambda x: x not in ("(R)", "(C)"), self.get_list_by_xpath(RANKING.TEAMS)
            )
        )
        ranking_rows = remove_qualification_relegation_and_css(
            self.get_list_by_xpath(RANKING.CURRENT_RANKING), teams
        )
        return ranking_rows

    def find_season_limit(self):
        """
        Find the season limit for the given league.

        Returns:
            int: The season limit for the given league.
        """
        season_limit_map = {
            "premier league": 1947,
            "la liga": 1929,
            "serie a": 1929,
            "ligue 1": 1945,
            "bundesliga": 1963,
        }
        return season_limit_map[self.league.lower()]

    def get_ranking_list(self) -> list:
        """
        Get the ranking list.

        Returns:
            list: The processed ranking data.
        """
        return self.ranking_list

    def get_ranking_csv(self, file_name: str, header: str = None) -> None:
        """
        Save the ranking data to a CSV file.

        Args:
            file_name (str): The name of the file to save the data to (without extension).
            header    (str): The header to include in the CSV file.
        """
        export_to_csv(file_name, self.ranking_list, header)

    def get_ranking_json(self, file_name: str, header: str = None) -> None:
        """
        Save the ranking data to a JSON file.

        Args:
            file_name (str): The name of the file to save the data to (without extension).
            header    (str): The header to include in the JSON file.
        """
        export_to_json(file_name, self.ranking_list, header_1=header)

    def get_ranking_dict(self, header: str = None) -> dict:
        """
        Get the ranking data as a dictionary.

        Args:
            header (str): The header to include in the dictionary. (Parent Key for the entire data)

        Returns:
            dict: The processed ranking data as a dictionary.
        """
        return export_to_dict(self.ranking_list, header_1=header)

    def get_ranking_pdf(self, file_name: str, dir="files") -> None:
        """
        Generate a PDF file containing the ranking table. Requires premier_league[pdf] to be installed.

        This method creates a formatted PDF file with the ranking table, including
        color-coded rows for European qualification spots and relegation.

        Args:
            file_name (str): The name of the file to save the PDF to (without extension).
            dir (str): The directory to save the PDF file to.
        """
        require_dependency("reportlab", "pdf")
        from reportlab.lib import colors
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A3
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.platypus import Table, TableStyle

        os.makedirs(dir, exist_ok=True)

        try:
            pdf = canvas.Canvas(f"{dir}/{file_name}.pdf", pagesize=A3)

            pdf.setFont("Helvetica", 16)
            title = f"{self.league} Table {self.season}"
            title_width = pdf.stringWidth(title, "Helvetica", 16)

            pdf.drawString((A3[0] - title_width) / 2 + 0.5, A3[1] - 30 + 0.1, title)
            pdf.drawString((A3[0] - title_width) / 2, A3[1] - 30, title)

            pdf.setFont("Helvetica", 12)
            table = Table(self.ranking_list)
            if int(self.season[:4]) >= 2021 and self.league == "Premier League":
                european_spots = self._find_european_qualification_spot()
            else:
                european_spots = self._scrap_european_qualification_spot()

            # 4 Teams were relegated in the 1994-95 season. Only Year to Ever Happen.
            relegation = -3
            if self.season == "1994-95":
                relegation = -4

            static_table_styles = [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#cccccc")),
                ("BACKGROUND", (0, 1), (-1, 4), HexColor("#aaff88")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, relegation), (-1, -1), HexColor("#e06666")),
            ]

            all_styles = static_table_styles + european_spots
            table.setStyle(TableStyle(all_styles))
            table.wrapOn(pdf, 0, 0)
            table_width, table_height = table.wrapOn(
                pdf, A3[0] - 2 * inch, A3[1] - 2 * inch
            )
            x = (A3[0] - table_width) / 2
            y = A3[1] - table_height - 1 * inch
            table.drawOn(pdf, x, y)

            pdf.save()
        except Exception:
            os.removedirs(dir)
            traceback.print_exc()

    def _find_european_qualification_spot(
        self,
    ) -> list[Union[tuple[str, tuple[int, int], tuple[int, int]], list]]:
        """
        Determine the European qualification spots for the current season.

        This method analyzes the current ranking and determines which teams qualify for
        various European competitions based on their league position and cup performances.

        Returns:
            list: A list of tuples containing styling information for the PDF table.
        """
        from reportlab.lib.colors import HexColor

        m_conference = None
        m_europa = []
        m_champions = []
        all_current_teams = [
            self.ranking_list[index][1] for index in range(1, len(self.ranking_list))
        ]
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
                uel_style.append(
                    ("BACKGROUND", (0, index), (-1, index), HexColor("#99cc00"))
                )
                europa_counter -= 1

        # Determine if Team already qualified to Champions League by League Position.
        for index in m_champions:
            if all_current_teams[index] not in cl_european_spots:
                cl_style.append(
                    ("BACKGROUND", (0, index), (-1, index), HexColor("#aaff88"))
                )

        # Determine if Conference League Qualifying Team already qualified to a higher Tournament
        if m_conference is not None:
            champions_matches = self._is_team_in_european_competition(
                m_conference, m_champions, all_current_teams
            )
            europa_matches = self._is_team_in_european_competition(
                m_conference, m_europa, all_current_teams
            )
            if (
                not champions_matches
                and not europa_matches
                and all_current_teams[m_conference] not in cl_european_spots
            ):
                uecl_style = (
                    "BACKGROUND",
                    (0, m_conference),
                    (-1, m_conference),
                    HexColor("#6aa84f"),
                )
                conference_counter -= 1

        # Determine if sixth place will receive Europa, Champions League or Europa Conference League spot
        index = 5
        while europa_counter > 0:
            if index in m_champions:
                index += 1
            if index in m_europa:
                index += 1
            else:
                uel_style.append(
                    ("BACKGROUND", (0, index), (-1, index), HexColor("#99cc00"))
                )
                europa_counter -= 1
                index += 1

        if conference_counter == 1:
            uecl_style = ("BACKGROUND", (0, index), (-1, index), HexColor("#6aa84f"))
        return [uecl_style] + uel_style + cl_style

    def _find_european_competition_spot(self) -> dict:
        """
        Find the winners of various competitions that may affect European qualification.

        This method scrapes data for FA Cup, EFL Cup, Champions League, Europa League,
        and Europa Conference League winners for the current season.

        Returns:
            dict: A dictionary containing the winners of each competition.
        """
        # FA Cup Winner for this Season (Potential Europa League Spot)
        fa_cup_page = self.additional_scrapper(
            f"https://en.wikipedia.org/wiki/{self.season}_FA_Cup"
        )
        fa_winner = self._find_tournament_winner(fa_cup_page, RANKING.CUP_WINNER)

        # EFL Cup Winner for this Season (Potential Europa Conference League Spot)
        efl_cup_page = self.additional_scrapper(
            f"https://en.wikipedia.org/wiki/{self.season}_EFL_Cup"
        )
        efl_winner = self._find_tournament_winner(efl_cup_page, RANKING.CUP_WINNER)

        # Previous Champions League Winner (Potential Champions League Spot)
        cl_page = self.additional_scrapper(
            f"https://en.wikipedia.org/wiki/{self.season}_UEFA_Champions_League"
        )
        cl_winner = self._find_tournament_winner(cl_page, RANKING.UEFA_WINNER)

        # Europa League Winner (Potential Champions League Spot)
        europa_page = self.additional_scrapper(
            f"https://en.wikipedia.org/wiki/{self.season}_UEFA_Europa_League"
        )
        europa_winner = self._find_tournament_winner(europa_page, RANKING.UEFA_WINNER)

        # Europa Conference League Winner (Potential Europa League Spot)
        conference_page = self.additional_scrapper(
            f"https://en.wikipedia.org/wiki/{self.season}_UEFA_Europa_Conference_League"
        )
        conference_winner = self._find_tournament_winner(
            conference_page, RANKING.UEFA_WINNER
        )

        return {
            "EFL": efl_winner,
            "FA": fa_winner,
            "CL": cl_winner,
            "UEL": europa_winner,
            "UECL": conference_winner,
        }

    def _scrap_european_qualification_spot(self) -> list:
        """
        Scrape European qualification spots for seasons prior to 2019-20.

        This method is used for older seasons where the qualification rules were different.

        Returns:
            list: A list of tuples containing styling information for the PDF table.
        """
        from reportlab.lib.colors import HexColor

        if int(self.season[:4]) == 1997:
            possible_european_spot = [
                "UEFA Cup",
                "Cup Winners' Cup",
                "Champions League",
                "UEFA Intertoto Cup",
            ]
        elif int(self.season[:4]) < 1997:
            possible_european_spot = [
                "UEFA Cup",
                "Cup Winners' Cup",
                "Champions League",
            ]
        elif int(self.season[:4]) <= 2007:
            possible_european_spot = ["UEFA Cup", "Intertoto Cup", "Champions League"]
        elif int(self.season[:4]) <= 2021:
            possible_european_spot = ["Champions League", "Europa League"]
        else:
            possible_european_spot = [
                "Champions League",
                "Europa League",
                "Europa Conference League",
            ]
        qualified = {}
        for tournament in possible_european_spot:
            qualified_teams = []
            teams = self.get_list_by_xpath(
                f'//tr[.//th/a[contains(text(), "{tournament}")]]/th/a/@title'
            )
            for item in teams:
                if "(" in item or ")" in item or "Fair Play" in item:
                    continue
                elif re.search(r"F\.C\.", item, flags=re.IGNORECASE):
                    qualified_teams.append(
                        re.sub(r"\s*F\.C\.\s*", " ", item, flags=re.IGNORECASE).strip()
                    )
                else:
                    qualified_teams.append(item)
            qualified[tournament] = qualified_teams
        style = []
        colors = [
            HexColor("#aaff88"),
            HexColor("#99cc00"),
            HexColor("#6aa84f"),
            HexColor("#e06666"),
        ]
        for index, tournament in enumerate(qualified.keys()):
            for team in qualified[tournament]:
                try:
                    team_index = self.ranking_list.index(
                        [i for i in self.ranking_list if team in i][0]
                    )
                except IndexError:
                    pass
                style.append(
                    ("BACKGROUND", (0, team_index), (-1, team_index), colors[index])
                )
        return style

    @staticmethod
    def _is_team_in_european_competition(team_index, competition_indices, all_teams):
        """
        Check if a team is already qualified for a European competition.

        Args:
            team_index (int): The index of the team to check.
            competition_indices (list): Indices of teams already qualified for a competition.
            all_teams (list): List of all teams in the current league.

        Returns:
            list: A list of indices where the team appears in the competition qualifiers.
        """
        return [i for i in competition_indices if all_teams[team_index] == all_teams[i]]

    @staticmethod
    def _find_tournament_winner(cup_page, xpath: str) -> str:
        """
        Find the winner of a specific tournament from a scraped page.

        Args:
            cup_page: The scraped page containing the tournament information.
            xpath (str): The XPath to locate the winner information.

        Returns:
            str: The name of the tournament winner, or None if not found.
        """
        result = cup_page.get_list_by_xpath(xpath)
        return result[0] if result else None
