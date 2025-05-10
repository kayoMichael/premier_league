import re
from datetime import datetime
from typing import Dict, List, Literal, Optional, Type, Union
from xml.etree.ElementTree import ElementTree

import pandas as pd
from lxml import etree
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.sql import exists

from premier_league.base import BaseDataSetScrapper

from ..data.initialize import init_db
from ..data.models import Game, GameStats, League, Team
from ..utils.url import PredictorURL
from ..utils.xpath import MATCHES


class MatchStatistics(BaseDataSetScrapper):
    """
    A class to scrape, process, and update MatchStatistics data for machine learning purposes.

    This class handles the retrieval of match data from specified URLs, processes game and player
    statistics from various tables, updates the underlying database, and allows exporting the data
    as a CSV file for further analysis or model training.
    """

    def __init__(
        self,
        db_filename: Optional[str] = "premier_league.db",
        db_directory: Optional[str] = "data",
    ):
        """
        Initialize the MatchStatistics instance.

        Sets up the current season, an empty list of URLs, initializes the database session,
        and fetches the current leagues information from the database.
        """
        super().__init__()
        self.current_season = None
        self.urls = []
        self.session = init_db(db_filename, db_directory)
        self.leagues = (
            self.session.query(League)
            .with_entities(
                League.name, League.up_to_date_season, League.up_to_date_match_week
            )
            .all()
        )

    def __calculate_team_stats(
        self,
        team: Team,
        game: Type[Game],
        lag: int,
        side: Literal["home", "away"] = "home",
    ) -> Union[dict[str, float], None]:
        """
        Calculate the Team Statistics with lag.
        team: (Team) the team query
        game: (Game) The Game Object
        side: (str) Home or Away
        """
        past_games = self.get_games_before_date(game.date, lag, team=team.name)
        same_season_games = list(
            filter(lambda past_game: past_game.get("season") == game.season, past_games)
        )

        if len(same_season_games) < lag:
            return None

        same_season_stats = [game["game_stats"] for game in same_season_games]
        stats_history = []

        for stats in same_season_stats:
            corresponding_team_stats = (
                stats[0] if stats[0]["team_id"] == team.id else stats[1]
            )
            if corresponding_team_stats["team_id"] == team.id:  # Safety check
                stats_history.append(corresponding_team_stats)

        n = len(stats_history)
        if n == 0:
            return None

        removal = ["id", "game_id", "team_id"]
        cleaned_up_history = [
            {k: v for k, v in stat.items() if k not in removal}
            for stat in stats_history
        ]

        return {
            f"{side}_{key}": sum(d[key] for d in cleaned_up_history) / n
            for key in cleaned_up_history[0].keys()
        }

    def create_dataset(self, output_path: str, rows_count: int = None, lag: int = 10):
        """
        Create a CSV file containing game statistics for machine learning training. Currently max of 17520 Data Rows.

        Each row in the CSV file represents one game, including both home and away team statistics.
        The data is sorted by date to maintain chronological order.

        Args:
            output_path (str): The file path where the CSV file will be saved.
            rows_count (int, optional): The maximum number of rows to include in the dataset. Defaults to None. if given gets the last n rows. after sorting by date.
            lag (int): The number of days to lag the data. 10 indicates, the current row will use the stats for the team's past 10 game average (Where all earlier games are dropped).
        Returns:
            None
        """
        if rows_count is not None and type(rows_count) != int:
            raise ValueError("rows_count must be an integer")
        elif rows_count is not None and rows_count < 0:
            raise ValueError("rows_count must be a positive integer")
        elif lag <= 0:
            raise ValueError("lag must be at least 1")

        query = self.session.query(Game).options(
            joinedload(Game.game_stats),
            joinedload(Game.home_team),
            joinedload(Game.away_team),
        )
        if rows_count is not None:
            query = query.order_by(Game.date.desc()).limit(rows_count)

        games = query.all()

        game_data = []

        for game in games:
            game_dict = {
                "game_id": game.id,
                "date": game.date,
                "season": game.season,
                "match_week": game.match_week,
                "home_team_id": game.home_team_id,
                "away_team_id": game.away_team_id,
                "home_team": game.home_team.name,
                "away_team": game.away_team.name,
                "home_goals": game.home_goals,
                "away_goals": game.away_goals,
                "home_points": game.home_team_points,
                "away_points": game.away_team_points,
            }

            # Construct Lag
            home_team = game.home_team
            away_team = game.away_team

            # Calculate stats for both teams
            home_stat = self.__calculate_team_stats(home_team, game, lag)
            away_stat = self.__calculate_team_stats(away_team, game, lag, side="away")

            if home_stat is None or away_stat is None:
                continue

            game_data.append({**game_dict, **home_stat, **away_stat})

        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(game_data)

        # Sort by date to maintain chronological order
        df = df.sort_values("date")

        # Move Target Columns to the end
        target_columns = ["home_goals", "away_goals"]
        df = df[df.columns.drop(target_columns).tolist() + target_columns]

        # Save to CSV
        df.to_csv(output_path, index=False)

    def match_statistic(self, season, team) -> List[Type[Game]]:
        """
        Retrieve match statistics for a given season or a specific team.

        If a team name is provided, returns a combined list of home and away games for that team.
        Otherwise, returns all games for the given season.

        Args:
            season (str): The season to query (e.g., "2021-2022").
            team (str or None): The name of the team to filter games. If None, returns all games for the season.

        Returns:
            List[Game]: A list of Game objects that match the query.
        """
        if team:
            team = (
                self.session.query(Team)
                .options(joinedload(Team.home_games), joinedload(Team.away_games))
                .filter(Team.name == team)
                .first()
            )
            return team.home_games + team.away_games
        return self.session.query(Game).filter_by(season=season).all()

    def get_all_leagues(self) -> List[str]:
        """
        Retrieve all leagues from the database.

        Returns:
            List[str]: A list of all League names in the database.
        """

        # since pylint cannot detect named tuples
        # pylint: disable=no-member
        return [league.name for league in self.leagues]

    def get_all_teams(self) -> List[str]:
        """
        Retrieve all teams from the database.

        Returns:
            List[str]: A list of all Team names in the database.
        """
        return [team.name for team in self.session.query(Team.name).all()]

    def get_team_games(self, team_name: str) -> List[Type[Game]]:
        """
        Retrieve all games for a specific team.

        Args:
            team_name (str): The name of the team to filter games.

        Returns:
            List[Game]: A list of Game objects that match the query.
        """
        team = self.session.query(Team).filter(Team.name == team_name).first()

        if not team:
            raise ValueError(f"No team found with name: {team_name}")

        games = (
            self.session.query(Game)
            .join(Team, or_(Game.home_team_id == Team.id, Game.away_team_id == Team.id))
            .filter(Team.name == team_name)
            .options(
                joinedload(Game.home_team),
                joinedload(Game.away_team),
                joinedload(Game.game_stats),
            )
            .all()
        )

        return [game.to_dict(include_relationships=True) for game in games]

    def get_total_game_count(self):
        """
        Retrieve the total number of games stored in the database.

        Returns:
            int: The total number of games in the database.
        """
        # pylint: disable=not-callable
        stmt = select(func.count()).select_from(
            Game
        )  # since pylint cannot detect proxy objects
        return self.session.execute(stmt).scalar_one()

    def get_games_by_season(self, season: str, match_week: int) -> List[dict]:
        """
        Retrieve all games for a specific season and match week.

        Args:
            season (str): The season to query (e.g., "2021-2022").
            match_week (str): The match week to filter games.

        Returns:
            List[Game]: A list of Game objects that match the query.
        """
        if not re.match(r"^\d{4}-\d{4}$", season):
            raise ValueError(
                "Invalid format for target_season. Please use 'YYYY-YYYY' (e.g., '2024-2025') with a regular hyphen."
            )
        games = (
            self.session.query(Game)
            .filter_by(season=season, match_week=match_week)
            .all()
        )

        if not games:
            raise ValueError(
                f"No games found for season: {season} and match week: {match_week}"
            )
        return [game.to_dict(include_relationships=True) for game in games]

    def get_games_before_date(
        self, date: datetime, limit: int = 10, team: Optional[str] = None
    ) -> List[dict]:
        """
        Retrieve games before a specific date with a limit. For a specific Team

        Args:
            date (datetime): The reference date.
            limit (int, optional): Maximum number of games to return. Defaults to 10.
            team (str, optional): The name of the team to filter games. Defaults to None.

        Returns:
            List[Game]: A list of Game objects before the given date, ordered by date descending.
        """
        query = self.session.query(Game).filter(Game.date < date)

        if team:
            team_id = self.session.query(Team.id).filter_by(name=team).scalar()
            if not team_id:
                raise ValueError(f"No team found with name: {team}")
            query = query.filter(
                (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
            )
        games = query.order_by(Game.date.desc()).limit(limit).all()

        return [game.to_dict(include_relationships=True) for game in games]

    def get_game_stats_before_date(
        self, date: datetime, limit: int = 10, team: Optional[str] = None
    ) -> List[dict]:
        """
        Retrieve game statistics before a specific date with a limit. For a specific Team

        Args:
            date (datetime): The reference date.
            limit (int, optional): Maximum number of games to return. Defaults to 10.
            team (str, optional): The name of the team to filter games. Defaults to None.
        Returns:
            List[dict]: List of game statistics dictionaries with relationships included.
            Returns empty list if no results found.
        """
        if not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object")

        query = self.session.query(GameStats).join(Game).filter(Game.date < date)

        if team:
            team_alias = aliased(Team)
            query = query.filter(
                exists().where(
                    (team_alias.id == GameStats.team_id) & (team_alias.name == team)
                )
            )

        stats = query.order_by(Game.date.desc()).limit(limit).all()

        return [stat.to_dict() for stat in stats] if stats else []

    def get_future_match(self, league: str, team=None) -> Union[Dict, str]:
        """
        Retrieve the next Match for a specific league and team (optional). This would return the team object of the future match.

        Args:
            league (str): The name of the league to retrieve the info (e.g., "Premier League").
            team (str, optional): The name of the team to filter games. Defaults to None.
        """
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        if current_month >= 8:
            self.current_season = f"{current_year}-{current_year + 1}"
        else:
            self.current_season = f"{current_year - 1}-{current_year}"

        if not team:

            def process_func(result, **kwargs):
                url = result.xpath(MATCHES.NEXT_MATCH_ROW)
                if len(url) == 0:
                    return "Current Season is finished! No more matches to play. For exiting games, please check the database. If they are not there. Run update_data_set(). Note: to extract match information from past games, please use get_games_before_date"
                match = re.search(r"/teams/([a-f0-9]+)/([a-f0-9]+)/", url[0])
                if match:
                    home_team_id = match.group(1)
                    away_team_id_ = match.group(2)

                    home_team = (
                        self.session.query(Team).filter_by(id=home_team_id).first()
                    )
                    away_team = (
                        self.session.query(Team).filter_by(id=away_team_id_).first()
                    )

                    return {"home_team": home_team, "away_team": away_team}
                return (
                    "Current Season is finished! No more matches to play. For exiting games, "
                    "please check the database. If they are not there. Run update_data_set(). "
                    "Note: to extract match information from past games, please use get_games_before_date()"
                )

        else:
            db_team = self.session.query(Team).filter_by(name=team).first()
            if not db_team:
                raise ValueError(
                    f"No team found with name: {team}. Please run get_all_teams() for all team names"
                )

            def process_func(result, **kwargs):
                urls = result.xpath(MATCHES.NEXT_MATCH_ROW)
                if len(urls) == 0:
                    return (
                        "Current Season is finished! No more matches to play. For exiting games, "
                        "please check the database. If they are not there. Run update_data_set(). "
                        "Note: to extract match information from past games, please use get_games_before_date()"
                    )
                for url in urls:
                    match = re.search(r"/teams/([a-f0-9]+)/([a-f0-9]+)/", url)
                    if match:
                        home_team_id = match.group(1)
                        away_team_id_ = match.group(2)
                        if home_team_id == db_team.id or away_team_id_ == db_team.id:
                            home_team = (
                                self.session.query(Team)
                                .filter_by(id=home_team_id)
                                .first()
                            )
                            away_team = (
                                self.session.query(Team)
                                .filter_by(id=away_team_id_)
                                .first()
                            )
                            return {"home_team": home_team, "away_team": away_team}

                return (
                    f"All matches for {team} are already played this season. "
                    f"Please check the database for existing games. If they are not there, "
                    f"run update_data_set() to fetch past games. Run get_team_games() to extract "
                    f"match information from past games"
                )

        result = self.scrape_and_process_all(
            [PredictorURL.get(self.current_season, league)],
            rate_limit=4,
            desc="Fetching Match Details",
            process_func=process_func,
        )[0]
        return result

    def update_data_set(self):
        """
        Update the dataset by scraping new game data and updating league information.
        This Method will Take a Considerable amount of time to run due to rate limit restrictions.

        This method:
            - Determines the current season based on the current date.
            - Constructs URLs for the seasons needing updates.
            - Scrapes the season schedule and filters out already-processed games.
            - Processes and adds new match details to the database.
            - Updates each league's up-to-date season and match week information.

        Returns:
            None
        """
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        if current_month >= 8:
            self.current_season = f"{current_year}-{current_year + 1}"
        else:
            self.current_season = f"{current_year - 1}-{current_year}"

        for league in self.leagues:
            # since pylint cannot detect named tuples
            update_to_date_year = int(
                # pylint: disable=no-member
                league.up_to_date_season.split("-")[0]
            )
            for i in range(update_to_date_year, int(self.current_season.split("-")[1])):
                url = PredictorURL.get(
                    f"{i}-{i + 1}", league.name  # pylint: disable=no-member
                )
                self.urls.append(url)

        self.pages = self.scrape_and_process_all(
            self.urls, rate_limit=4, desc="Fetching Season Schedule"
        )
        relevant_urls = self._process_up_to_date_url()
        filtered_urls = []
        for url in relevant_urls:
            game_id = re.search(r"/matches/([a-f0-9]+)/", url).group(1)
            game = self.session.query(Game).filter_by(id=game_id).first()
            if not game:
                filtered_urls.append(url)

        if not filtered_urls:
            print("All Data is up to Date!")
            return

        self.scrape_and_process_all(
            filtered_urls,
            rate_limit=4,
            desc="Fetching Match Details",
            process_func=self._process_data,
        )
        latest_seasons = (
            self.session.query(League.name, func.max(Game.season).label("max_season"))
            .join(Game)
            .group_by(League.name)
            .subquery()
        )
        latest_games = (
            self.session.query(
                League.name,
                Game.season,
                func.max(Game.match_week).label("latest_match_week"),
            )
            .join(Game)
            .join(
                latest_seasons,
                and_(
                    League.name == latest_seasons.c.name,
                    Game.season == latest_seasons.c.max_season,
                ),
            )
            .group_by(League.name, Game.season)
            .order_by(Game.season.desc(), func.max(Game.match_week).desc())
            .all()
        )

        # Update League Updated Date Index
        for league, season, latest_match_week in latest_games:
            league_obj = self.session.query(League).filter_by(name=league).first()
            league_obj.up_to_date_season = season
            league_obj.up_to_date_match_week = latest_match_week
        self.session.commit()
        print("Data Updated!")

    def _process_up_to_date_url(self):
        """
        Process and filter URLs based on current league information.

        Extracts season and league name from page titles and uses this information
        to determine which match report URLs are up-to-date or require updates.

        Returns:
            List[str]: A list of fully qualified URLs for match reports that need processing.
        """
        title_map = self.process_xpath("//h1//text()", show_progress=False)
        leagues_dict = {league[0]: (league[1], league[2]) for league in self.leagues}
        all_urls = []
        for index, page in enumerate(self.pages):
            title = title_map[index]
            pattern = r"(\d{4}-\d{4})\s+(.*?)\s+Scores"
            match = re.search(pattern, title)

            relevant_xpath = MATCHES.match_report_url()
            if match:
                season = match.group(1)
                league = match.group(2)

                if league == "Bundesliga":
                    league = "Fußball-Bundesliga"

                if league == "Championship":
                    league = "EFL Championship"

                if season == leagues_dict[league][0]:
                    relevant_xpath = MATCHES.match_report_url(
                        match_week=leagues_dict[league][1]
                    )

            all_urls.extend(
                [f"https://fbref.com{url}" for url in page.xpath(relevant_xpath)]
            )
        return all_urls

    @staticmethod
    def _wrap_result_with_url(
        result: ElementTree, url: str, **kwargs
    ) -> Union[tuple, None]:
        """
        Wrap the result with its corresponding URL.

        Args:
            result (ElementTree): The parsed XML/HTML tree result.
            url (str): The URL from which the result was fetched.
            **kwargs: Additional keyword arguments (unused).

        Returns:
            tuple or None: A tuple (result, url) if the result is valid; otherwise, None.
        """
        if result:
            return result, url
        return None

    @staticmethod
    def _return_by_position_data(table) -> tuple:
        """
        Process a DataFrame of player positions and group the data by primary position.

        Splits the 'Pos' column to extract the primary position and assigns players to
        specific position groups: forwards (ST), midfielders (MF), defenders (DF), and an aggregate group.

        Args:
            table (pd.DataFrame): A DataFrame containing player statistics with a 'Pos' column.

        Returns:
            tuple: A tuple containing DataFrames for forwards (FW), midfielders (MF), defenders (DF),
                   and an aggregate DataFrame.
        """
        table["Primary_Position"] = table["Pos"].str.split(",").str[0]
        table["Position_Group"] = table["Primary_Position"].apply(
            lambda x: (
                "ST"
                if any(pos in str(x) for pos in ["FW", "LW", "RW", "AM"])
                else (
                    "MF"
                    if any(pos in str(x) for pos in ["CM", "DM", "RM", "LM"])
                    else (
                        "DF"
                        if any(pos in str(x) for pos in ["CB", "LB", "RB"])
                        else "GK"
                        if "GK" in str(x)
                        else "Total"
                    )
                )
            )
        )
        grouped_players = table.groupby("Position_Group")
        FW = grouped_players.get_group("ST")
        MF = grouped_players.get_group("MF")
        DF = grouped_players.get_group("DF")
        aggregate = grouped_players.get_group("Total")
        return FW, MF, DF, aggregate

    def _fetch_corresponding_data_from_table(
        self,
        summary_table: pd.DataFrame,
        passing_table: pd.DataFrame,
        defence_table: pd.DataFrame,
        possession_table: pd.DataFrame,
        miscellaneous_table: pd.DataFrame,
        goal_keeper_table: pd.DataFrame,
        possession: int,
    ) -> dict:
        """
        Extract and aggregate game statistics from multiple DataFrame tables.

        Processes tables containing summary, passing, defensive, possession, miscellaneous,
        and goalkeeper statistics. Aggregates relevant metrics and returns a dictionary of computed values.

        Args:
            summary_table (pd.DataFrame): DataFrame containing summary statistics.
            passing_table (pd.DataFrame): DataFrame containing passing statistics.
            defence_table (pd.DataFrame): DataFrame containing defensive statistics.
            possession_table (pd.DataFrame): DataFrame containing possession statistics.
            miscellaneous_table (pd.DataFrame): DataFrame containing miscellaneous statistics.
            goal_keeper_table (pd.DataFrame): DataFrame containing goalkeeper statistics.
            possession (int): The team's possession percentage.

        Returns:
            dict: A dictionary containing aggregated game statistics.
        """
        data = {}

        (
            ST_summary,
            MF_summary,
            DF_summary,
            aggregate_summary,
        ) = self._return_by_position_data(summary_table)
        data.update(
            {
                "xG": aggregate_summary["xG"].sum().item(),
                "xAG": aggregate_summary["xAG"].sum().item(),
                "shots_total_FW": ST_summary["Sh"].sum().item(),
                "shots_total_MF": MF_summary["Sh"].sum().item(),
                "shots_total_DF": DF_summary["Sh"].sum().item(),
                "shots_on_target_FW": ST_summary["SoT"].sum().item(),
                "shots_on_target_MF": MF_summary["SoT"].sum().item(),
                "shots_on_target_DF": DF_summary["SoT"].sum().item(),
                "shot_creating_chances_FW": ST_summary["SCA"].sum().item(),
                "shot_creating_chances_MF": MF_summary["SCA"].sum().item(),
                "shot_creating_chances_DF": DF_summary["SCA"].sum().item(),
                "goal_creating_actions_FW": ST_summary["GCA"].sum().item(),
                "goal_creating_actions_MF": MF_summary["GCA"].sum().item(),
                "goal_creating_actions_DF": DF_summary["GCA"].sum().item(),
            }
        )

        (
            ST_passing,
            MF_passing,
            DF_passing,
            aggregate_passing,
        ) = self._return_by_position_data(passing_table)
        data.update(
            {
                "passes_completed_FW": ST_passing["Cmp"].sum().item(),
                "passes_completed_MF": MF_passing["Cmp"].sum().item(),
                "passes_completed_DF": DF_passing["Cmp"].sum().item(),
                "xA": aggregate_passing["xA"].sum().item(),
                "pass_completion_percentage_FW": ST_passing["Cmp%"].mean(),
                "pass_completion_percentage_MF": MF_passing["Cmp%"].mean(),
                "pass_completion_percentage_DF": DF_passing["Cmp%"].mean(),
                "key_passes": aggregate_passing["KP"].sum().item(),
                "passes_into_final_third": aggregate_passing["1/3"].sum().item(),
                "passes_into_penalty_area": aggregate_passing["PPA"].sum().item(),
                "crosses_into_penalty_area": aggregate_passing["CrsPA"].sum().item(),
                "progressive_passes": aggregate_passing["PrgP"].sum().item(),
            }
        )

        (
            ST_defence,
            MF_defence,
            DF_defence,
            aggregate_defence,
        ) = self._return_by_position_data(defence_table)
        data.update(
            {
                "tackles_won_FW": ST_defence["TklW"].sum().item(),
                "tackles_won_MF": MF_defence["TklW"].sum().item(),
                "tackles_won_DF": DF_defence["TklW"].sum().item(),
                "dribblers_challenged_won_FW": ST_defence["Tkl.1"].sum().item(),
                "dribblers_challenged_won_MF": MF_defence["Tkl.1"].sum().item(),
                "dribblers_challenged_won_DF": DF_defence["Tkl.1"].sum().item(),
                "blocks_FW": ST_defence["Blocks"].sum().item(),
                "blocks_MF": MF_defence["Blocks"].sum().item(),
                "blocks_DF": DF_defence["Blocks"].sum().item(),
                "interceptions_FW": ST_defence["Int"].sum().item(),
                "interceptions_MF": MF_defence["Int"].sum().item(),
                "interceptions_DF": DF_defence["Int"].sum().item(),
                "clearances_FW": ST_defence["Clr"].sum().item(),
                "clearances_MF": MF_defence["Clr"].sum().item(),
                "clearances_DF": DF_defence["Clr"].sum().item(),
                "errors_leading_to_goal": aggregate_defence["Err"].sum().item(),
            }
        )

        (
            ST_possession,
            MF_possession,
            DF_possession,
            aggregate_possession,
        ) = self._return_by_position_data(possession_table)
        data.update(
            {
                "possession_rate": possession,
                "touches_FW": ST_possession["Touches"].sum().item(),
                "touches_MF": MF_possession["Touches"].sum().item(),
                "touches_DF": DF_possession["Touches"].sum().item(),
                "touches_att_pen_area_FW": ST_possession["Att Pen"].sum().item(),
                "touches_att_pen_area_MF": MF_possession["Att Pen"].sum().item(),
                "touches_att_pen_area_DF": DF_possession["Att Pen"].sum().item(),
                "take_ons_FW": ST_possession["Att"].sum().item(),
                "take_ons_MF": MF_possession["Att"].sum().item(),
                "take_ons_DF": DF_possession["Att"].sum().item(),
                "successful_take_ons_FW": ST_possession["Succ"].sum().item(),
                "successful_take_ons_MF": MF_possession["Succ"].sum().item(),
                "successful_take_ons_DF": DF_possession["Succ"].sum().item(),
                "carries_FW": ST_possession["Carries"].sum().item(),
                "carries_MF": MF_possession["Carries"].sum().item(),
                "carries_DF": DF_possession["Carries"].sum().item(),
                "total_carrying_distance_FW": ST_possession["TotDist"].sum().item(),
                "total_carrying_distance_MF": MF_possession["TotDist"].sum().item(),
                "total_carrying_distance_DF": DF_possession["TotDist"].sum().item(),
                "dispossessed_FW": ST_possession["Dis"].sum().item(),
                "dispossessed_MF": MF_possession["Dis"].sum().item(),
                "dispossessed_DF": DF_possession["Dis"].sum().item(),
                "miss_controlled_FW": ST_possession["Mis"].sum().item(),
                "miss_controlled_MF": MF_possession["Mis"].sum().item(),
                "miss_controlled_DF": DF_possession["Mis"].sum().item(),
                "carries_into_penalty_area": aggregate_possession["CPA"].sum().item(),
            }
        )

        (
            ST_miscellaneous,
            MF_miscellaneous,
            DF_miscellaneous,
            aggregate_miscellaneous,
        ) = self._return_by_position_data(miscellaneous_table)
        data.update(
            {
                "fouls_committed_FW": ST_miscellaneous["Fls"].sum().item(),
                "fouls_committed_MF": MF_miscellaneous["Fls"].sum().item(),
                "fouls_committed_DF": DF_miscellaneous["Fls"].sum().item(),
                "fouls_drawn_FW": ST_miscellaneous["Fld"].sum().item(),
                "fouls_drawn_MF": MF_miscellaneous["Fld"].sum().item(),
                "fouls_drawn_DF": DF_miscellaneous["Fld"].sum().item(),
                "offside_FW": ST_miscellaneous["Off"].sum().item(),
                "offside_MF": MF_miscellaneous["Off"].sum().item(),
                "offside_DF": DF_miscellaneous["Off"].sum().item(),
                "pens_won": aggregate_miscellaneous["PKwon"].sum().item(),
                "pens_conceded": aggregate_miscellaneous["PKcon"].sum().item(),
                "aerials_won_FW": ST_miscellaneous["Won"].sum().item(),
                "aerials_won_MF": MF_miscellaneous["Won"].sum().item(),
                "aerials_won_DF": DF_miscellaneous["Won"].sum().item(),
                "aerials_lost_FW": ST_miscellaneous["Lost"].sum().item(),
                "aerials_lost_MF": MF_miscellaneous["Lost"].sum().item(),
                "aerials_lost_DF": DF_miscellaneous["Lost"].sum().item(),
                "yellow_card": aggregate_miscellaneous["CrdY"].sum().item(),
                "red_card": aggregate_miscellaneous["CrdR"].sum().item(),
            }
        )
        data.update(
            {
                "save_percentage": goal_keeper_table["Save%"].mean(),
                "saves": goal_keeper_table["Saves"].sum().item(),
                "PSxG": goal_keeper_table["PSxG"].sum().item(),
                "passes_completed_GK": goal_keeper_table["Att (GK)"].sum().item(),
                "passes_40_yard_completed_GK": goal_keeper_table["Cmp"].sum().item(),
                "crosses_stopped": goal_keeper_table["Stp"].sum().item(),
            }
        )

        return data

    def _process_data(self, page, **kwargs):
        """
        Process a scraped match page to extract and store game and statistics data.

        Extracts game information such as teams, scores, match date/time, and detailed statistics from various tables.
        If the game data does not exist in the database, it creates new records for the league, teams, game,
        and the associated game statistics.

        Args:
            page: The scraped HTML page (as an lxml element) containing match data.
            **kwargs: Additional keyword arguments, including:
                      - url (str): The URL of the page being processed.

        Returns:
            None

        Raises:
            Exception: If an error occurs while adding match data to the database.
        """
        try:
            url = kwargs.get("url")
            game_id = re.search(r"/matches/([a-f0-9]+)/", url).group(1)

            game = self.session.query(Game).filter_by(id=game_id).first()
            if game:
                return

            try:
                league_name, match_week_unrefined = page.xpath(MATCHES.GAME_HEADER)[0:2]
                match_week = int(
                    re.search(r"Matchweek (\d+)", match_week_unrefined).group(1)
                )
            except Exception:
                league_name = "Major League Soccer"
                match_week = 0

            home_stats, away_stats = page.xpath(MATCHES.GAME_STATS)[0:2]
            home_team_name = home_stats.xpath(MATCHES.A_TAG)[0]
            home_team_id = re.search(
                r"/squads/([^/]+)/", home_stats.xpath(".//a//@href")[0]
            ).group(1)
            away_team_name = away_stats.xpath(MATCHES.A_TAG)[0]
            away_team_id = re.search(
                r"/squads/([^/]+)/", away_stats.xpath(".//a//@href")[0]
            ).group(1)
            home_team_record = home_stats.xpath("./div")[2].text
            home_team_points = sum(
                x * y
                for x, y in zip(
                    (3, 1, 0), (int(n) for n in home_team_record.split("-"))
                )
            )
            away_team_record = away_stats.xpath("./div")[2].text
            away_team_points = sum(
                x * y
                for x, y in zip(
                    (3, 1, 0), (int(n) for n in away_team_record.split("-"))
                )
            )
            match_info = page.xpath(MATCHES.GAME_STATS)[2]
            match_date = match_info.xpath("./div")[0].xpath(MATCHES.GAME_VENUE_DATE)[0]
            current_year = int(match_date.split("-")[0])
            current_season = (
                f"{current_year - 1}-{current_year}"
                if int(match_date.split("-")[1]) < 8
                else f"{current_year}-{current_year + 1}"
            )
            match_venue_time = match_info.xpath("./div")[0].xpath(
                MATCHES.GAME_VENUE_TIME
            )[0]
            match_time = datetime.strptime(
                f"{match_date} {match_venue_time}", "%Y-%m-%d %H:%M"
            )
            home_goals = int(home_stats.xpath(MATCHES.GAME_GOALS)[0])
            away_goals = int(away_stats.xpath(MATCHES.GAME_GOALS)[0])

            tables = page.xpath("//table")
            home_possession = int(
                pd.read_html(etree.tostring(tables[2]), header=1)[0]
                .iloc[0]
                .iat[0]
                .replace("%", "")
            )
            away_possession = int(
                pd.read_html(etree.tostring(tables[2]), header=1)[0]
                .iloc[0]
                .iat[1]
                .replace("%", "")
            )
            summary_table = pd.read_html(etree.tostring(tables[3]), header=1)[0]
            passing_table = pd.read_html(etree.tostring(tables[4]), header=1)[0]
            defence_table = pd.read_html(etree.tostring(tables[6]), header=1)[0]
            possession_table = pd.read_html(etree.tostring(tables[7]), header=1)[0]
            miscellaneous_table = pd.read_html(etree.tostring(tables[8]), header=1)[0]
            goal_keeper_table = pd.read_html(etree.tostring(tables[9]), header=1)[0]

            team_data_one = self._fetch_corresponding_data_from_table(
                summary_table,
                passing_table,
                defence_table,
                possession_table,
                miscellaneous_table,
                goal_keeper_table,
                home_possession,
            )

            summary_table = pd.read_html(etree.tostring(tables[10]), header=1)[0]
            passing_table = pd.read_html(etree.tostring(tables[11]), header=1)[0]
            defence_table = pd.read_html(etree.tostring(tables[13]), header=1)[0]
            possession_table = pd.read_html(etree.tostring(tables[14]), header=1)[0]
            miscellaneous_table = pd.read_html(etree.tostring(tables[15]), header=1)[0]
            goal_keeper_table = pd.read_html(etree.tostring(tables[16]), header=1)[0]

            team_data_two = self._fetch_corresponding_data_from_table(
                summary_table,
                passing_table,
                defence_table,
                possession_table,
                miscellaneous_table,
                goal_keeper_table,
                away_possession,
            )
        except Exception as e:
            print(f"Error processing match data: {str(e)}")
            print("Error URL: ", url)
            return

        try:
            league = self.session.query(League).filter_by(name=league_name).first()
            if not league:
                league = League(
                    name=league_name,
                    up_to_date_season="2018-2019",
                    up_to_date_match_week=match_week,
                )
                self.session.add(league)
                self.session.flush()

            home_team = (
                self.session.query(Team)
                .filter_by(
                    id=home_team_id,
                )
                .first()
            )
            if not home_team:
                home_team = Team(
                    id=home_team_id, name=home_team_name, league_id=league.id
                )
                self.session.add(home_team)

            away_team = (
                self.session.query(Team)
                .filter_by(
                    id=away_team_id,
                )
                .first()
            )
            if not away_team:
                away_team = Team(
                    id=away_team_id, name=away_team_name, league_id=league.id
                )
                self.session.add(away_team)

            self.session.flush()

            game = Game(
                id=game_id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                league_id=league.id,
                home_team_points=home_team_points,
                away_team_points=away_team_points,
                home_goals=home_goals,
                away_goals=away_goals,
                date=match_time,
                match_week=match_week,
                season=current_season,
            )
            self.session.add(game)
            self.session.flush()

            home_statistics = GameStats(
                game_id=game.id, team_id=home_team.id, **team_data_one
            )
            away_statistics = GameStats(
                game_id=game.id, team_id=away_team.id, **team_data_two
            )
            self.session.add(home_statistics)
            self.session.add(away_statistics)

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error adding match data: {str(e)}")
