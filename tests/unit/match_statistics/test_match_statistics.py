from datetime import datetime
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, patch

import pytest

from premier_league.data.models import Game, GameStats, Team
from premier_league.match_statistics.match_statistics import MatchStatistics


@pytest.fixture
def mock_init_db():
    """Fixture to mock the database initialization function."""
    with patch("premier_league.match_statistics.match_statistics.init_db") as mock:
        session_mock = MagicMock()
        mock.return_value = session_mock
        yield mock, session_mock


@pytest.fixture
def mock_base_scrapper():
    """Fixture to mock the BaseDataSetScrapper parent class."""
    with patch(
        "premier_league.match_statistics.match_statistics.BaseDataSetScrapper.__init__",
        return_value=None,
    ):
        yield


@pytest.fixture
def match_statistics(mock_init_db, mock_base_scrapper):
    """Fixture to create a MatchStatistics instance with mocked dependencies."""
    _, session_mock = mock_init_db

    leagues_result = [("Premier League", "2021-2022", 38), ("La Liga", "2021-2022", 38)]
    session_mock.query.return_value.with_entities.return_value.all.return_value = (
        leagues_result
    )

    # Create instance
    stats = MatchStatistics()
    stats.session = session_mock
    stats.current_season = None
    stats.urls = []
    stats.leagues = leagues_result

    return stats


class TestMatchStatistics:
    """Test suite for the MatchStatistics class."""

    def test_initialization(self, mock_init_db):
        """Test that the MatchStatistics class initializes correctly."""
        mock_db, session_mock = mock_init_db

        leagues_result = [("Premier League", "2021-2022", 38)]
        session_mock.query.return_value.with_entities.return_value.all.return_value = (
            leagues_result
        )

        with patch(
            "premier_league.match_statistics.match_statistics.BaseDataSetScrapper.__init__",
            return_value=None,
        ):
            match_stats = MatchStatistics()
            assert match_stats.current_season is None
            assert match_stats.urls == []
            assert mock_db.called
            assert session_mock.query.called

    def test_create_dataset(self, match_statistics):
        """Test that create_dataset properly processes game data and creates a CSV file."""
        home_team = MagicMock()
        home_team.name = "Arsenal"
        away_team = MagicMock()
        away_team.name = "Chelsea"

        home_stats = MagicMock()
        home_stats.team_id = "arsenal_id"
        home_stats.possession_rate = 60
        home_stats.xG = 2.5

        away_stats = MagicMock()
        away_stats.team_id = "chelsea_id"
        away_stats.possession_rate = 40
        away_stats.xG = 1.2

        game = MagicMock()
        game.id = "game_id"
        game.date = datetime(2022, 5, 1)
        game.season = "2021-2022"
        game.match_week = 36
        game.home_team = home_team
        game.away_team = away_team
        game.home_team_id = "arsenal_id"
        game.away_team_id = "chelsea_id"
        game.home_goals = 3
        game.away_goals = 1
        game.home_team_points = 3
        game.away_team_points = 0
        game.game_stats = [home_stats, away_stats]

        match_statistics.session.query.return_value.options.return_value.all.return_value = [
            game
        ]
        match_statistics._MatchStatistics__calculate_team_stats = MagicMock()
        match_statistics._MatchStatistics__calculate_team_stats.side_effect = [
            {"home_stat1": 10, "home_stat2": 20},
            {"away_stat1": 5, "away_stat2": 15},
        ]

        with patch(
            "premier_league.match_statistics.match_statistics.pd.DataFrame"
        ) as mock_df:
            df_instance = MagicMock()
            mock_df.return_value = df_instance

            # Configure the columns attribute for the drop operation
            columns_mock = MagicMock()
            df_instance.columns = columns_mock
            columns_drop_result = MagicMock()
            columns_mock.drop.return_value = columns_drop_result
            columns_drop_result.tolist.return_value = ["other_column1", "other_column2"]
            df_instance.sort_values.return_value = df_instance
            df_instance.__getitem__.return_value = df_instance
            match_statistics.create_dataset("test_output.csv")

            match_statistics.session.query.assert_any_call(Game)
            mock_df.assert_called_once()
            df_instance.sort_values.assert_called_once_with("date")
            columns_mock.drop.assert_called_once()  # Verify columns.drop was called
            df_instance.to_csv.assert_called_once_with("test_output.csv", index=False)

    def test_create_dataset_with_rows_limit(self, match_statistics):
        """Test create_dataset with a row count limit."""
        match_statistics.session.query.return_value.options.return_value.order_by.return_value.limit.return_value.all.return_value = (
            []
        )

        with patch(
            "premier_league.match_statistics.match_statistics.pd.DataFrame"
        ) as mock_df:
            df_instance = MagicMock()
            mock_df.return_value = df_instance
            df_instance.sort_values.return_value = df_instance
            match_statistics.session.reset_mock()
            match_statistics.create_dataset("test_output.csv", rows_count=100)
            match_statistics.session.query.assert_any_call(Game)
            match_statistics.session.query.return_value.options.return_value.order_by.assert_called_once_with(
                ANY
            )
            match_statistics.session.query.return_value.options.return_value.order_by.return_value.limit.assert_called_once_with(
                100
            )

    def test_create_dataset_invalid_rows_count(self, match_statistics):
        """Test create_dataset with invalid rows_count parameter."""
        with pytest.raises(ValueError, match="rows_count must be an integer"):
            match_statistics.create_dataset("test_output.csv", rows_count="100")

        with pytest.raises(ValueError, match="rows_count must be a positive integer"):
            match_statistics.create_dataset("test_output.csv", rows_count=-10)

    def test_match_statistic_with_team(self, match_statistics):
        """Test match_statistic method with a team parameter."""
        team = MagicMock()
        team.home_games = ["Manchester United", "NewCastle United"]
        team.away_games = ["Nottingham Forest FC"]
        match_statistics.session.query.return_value.options.return_value.filter.return_value.first.return_value = (
            team
        )

        result = match_statistics.match_statistic("2021-2022", "Arsenal")
        match_statistics.session.query.assert_any_call(Team)
        match_statistics.session.query.return_value.options.assert_called_once()
        match_statistics.session.query.return_value.options.return_value.filter.assert_called_once_with(
            ANY
        )
        assert result == [
            "Manchester United",
            "NewCastle United",
            "Nottingham Forest FC",
        ]

    def test_match_statistic_without_team(self, match_statistics):
        """Test match_statistic method without a team parameter."""
        games = ["game1", "game2"]
        match_statistics.session.query.return_value.filter_by.return_value.all.return_value = (
            games
        )
        result = match_statistics.match_statistic("2021-2022", None)
        match_statistics.session.query.assert_any_call(Game)
        match_statistics.session.query.return_value.filter_by.assert_called_once_with(
            season="2021-2022"
        )
        assert result == games

    def test_get_all_leagues(self, match_statistics):
        """Test get_all_leagues method returns all league names."""
        match_statistics.leagues = [
            SimpleNamespace(**{"name": "Premier League"}),
            SimpleNamespace(**{"name": "La Liga"}),
            SimpleNamespace(**{"name": "Serie A"}),
            SimpleNamespace(**{"name": "Bundesliga"}),
        ]
        result = match_statistics.get_all_leagues()
        assert result == ["Premier League", "La Liga", "Serie A", "Bundesliga"]

    def test_get_all_teams(self, match_statistics):
        """Test get_all_teams method returns all team names."""
        match_statistics.session.query.return_value.all.return_value = [
            SimpleNamespace(**{"name": "Arsenal"}),
            SimpleNamespace(**{"name": "Chelsea"}),
            SimpleNamespace(**{"name": "Manchester City"}),
        ]
        result = match_statistics.get_all_teams()
        match_statistics.session.query.assert_any_call(ANY)
        assert result == ["Arsenal", "Chelsea", "Manchester City"]

    def test_get_team_games(self, match_statistics):
        """Test get_team_games method returns games for a specific team."""
        team = MagicMock()
        team.id = "team_id"
        match_statistics.session.query.return_value.filter.return_value.first.return_value = (
            team
        )

        game1 = MagicMock()
        game1.to_dict.return_value = {"id": "game1", "home_team": "Arsenal"}
        game2 = MagicMock()
        game2.to_dict.return_value = {"id": "game2", "away_team": "Arsenal"}

        match_statistics.session.query.return_value.join.return_value.filter.return_value.options.return_value.all.return_value = [
            game1,
            game2,
        ]

        result = match_statistics.get_team_games("Arsenal")
        match_statistics.session.query.assert_any_call(Team)
        match_statistics.session.query.return_value.filter.assert_any_call(ANY)
        match_statistics.session.query.assert_any_call(Game)
        assert result == [
            {"id": "game1", "home_team": "Arsenal"},
            {"id": "game2", "away_team": "Arsenal"},
        ]

    def test_get_team_games_team_not_found(self, match_statistics):
        """Test get_team_games raises an error when team is not found."""
        match_statistics.session.query.return_value.filter.return_value.first.return_value = (
            None
        )
        with pytest.raises(
            ValueError, match="No team found with name: NonexistentTeam"
        ):
            match_statistics.get_team_games("NonexistentTeam")

    def test_get_total_game_count(self, match_statistics):
        """Test the get_total_game_count method."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 123
        match_statistics.session.execute.return_value = mock_result
        count = match_statistics.get_total_game_count()
        assert count == 123

    def test_get_games_by_season(self, match_statistics):
        """Test get_games_by_season returns games for a specific season and match week."""
        game1 = MagicMock()
        game1.to_dict.return_value = {
            "id": "game1",
            "season": "2021-2022",
            "match_week": 1,
        }
        game2 = MagicMock()
        game2.to_dict.return_value = {
            "id": "game2",
            "season": "2021-2022",
            "match_week": 1,
        }

        match_statistics.session.query.return_value.filter_by.return_value.all.return_value = [
            game1,
            game2,
        ]
        result = match_statistics.get_games_by_season("2021-2022", 1)
        match_statistics.session.query.assert_any_call(Game)
        match_statistics.session.query.return_value.filter_by.assert_called_once_with(
            season="2021-2022", match_week=1
        )
        assert result == [
            {"id": "game1", "season": "2021-2022", "match_week": 1},
            {"id": "game2", "season": "2021-2022", "match_week": 1},
        ]

    def test_get_games_by_season_invalid_format(self, match_statistics):
        """Test get_games_by_season raises an error with invalid season format."""
        with pytest.raises(ValueError, match="Invalid format for target_season"):
            match_statistics.get_games_by_season("20212022", 1)

    def test_get_games_by_season_no_games(self, match_statistics):
        """Test get_games_by_season raises an error when no games are found."""
        match_statistics.session.query.return_value.filter_by.return_value.all.return_value = (
            []
        )

        with pytest.raises(
            ValueError, match="No games found for season: 2021-2022 and match week: 1"
        ):
            match_statistics.get_games_by_season("2021-2022", 1)

    def test_get_games_before_date(self, match_statistics):
        """Test get_games_before_date returns games before a specific date."""
        game1 = MagicMock()
        game1.to_dict.return_value = {"id": "game1", "date": datetime(2022, 4, 15)}
        game2 = MagicMock()
        game2.to_dict.return_value = {"id": "game2", "date": datetime(2022, 4, 10)}

        match_statistics.session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            game1,
            game2,
        ]
        test_date = datetime(2022, 5, 1)
        result = match_statistics.get_games_before_date(test_date, limit=5)
        match_statistics.session.query.assert_any_call(Game)
        match_statistics.session.query.return_value.filter.assert_called_once()
        match_statistics.session.query.return_value.filter.return_value.order_by.assert_called_once()
        match_statistics.session.query.return_value.filter.return_value.order_by.return_value.limit.assert_called_once_with(
            5
        )
        assert result == [
            {"id": "game1", "date": datetime(2022, 4, 15)},
            {"id": "game2", "date": datetime(2022, 4, 10)},
        ]

    def test_get_games_before_date_with_team(self, match_statistics):
        """Test get_games_before_date with team filter."""
        team_id = "arsenal_id"
        query_team_mock = MagicMock()
        query_team_mock.filter_by.return_value.scalar.return_value = team_id

        game = MagicMock()
        game.to_dict.return_value = {"id": "game1", "home_team": "Arsenal"}

        query_game_mock = MagicMock()
        query_game_mock.filter.return_value = query_game_mock
        query_game_mock.order_by.return_value = query_game_mock
        query_game_mock.limit.return_value = query_game_mock
        query_game_mock.all.return_value = [game]

        def query_side_effect(*args, **kwargs):
            print("query args:", args)
            if args and args[0] is Team.id:
                return query_team_mock
            elif args and args[0] is Game:
                return query_game_mock
            else:
                raise ValueError(f"Unexpected query argument(s): {args}")

        match_statistics.session.query.side_effect = query_side_effect
        test_date = datetime(2022, 5, 1)
        result = match_statistics.get_games_before_date(
            test_date, limit=5, team="Arsenal"
        )
        query_team_mock.filter_by.assert_called_once_with(name="Arsenal")
        match_statistics.session.query.assert_any_call(Game)
        assert result == [{"id": "game1", "home_team": "Arsenal"}]

    def test_get_game_stats_before_date(self, match_statistics):
        """Test get_game_stats_before_date returns stats before a specific date."""
        stat1 = MagicMock()
        stat1.to_dict.return_value = {"id": "stat1", "xG": 2.5}
        stat2 = MagicMock()
        stat2.to_dict.return_value = {"id": "stat2", "xG": 1.8}

        match_statistics.session.query.return_value.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            stat1,
            stat2,
        ]

        test_date = datetime(2022, 5, 1)
        result = match_statistics.get_game_stats_before_date(test_date)
        match_statistics.session.query.assert_any_call(GameStats)
        match_statistics.session.query.return_value.join.assert_called_once_with(Game)
        match_statistics.session.query.return_value.join.return_value.filter.assert_called_once()
        assert result == [{"id": "stat1", "xG": 2.5}, {"id": "stat2", "xG": 1.8}]

    def test_get_game_stats_before_date_invalid_date(self, match_statistics):
        """Test get_game_stats_before_date raises error with invalid date type."""
        with pytest.raises(ValueError, match="Date must be a datetime object"):
            match_statistics.get_game_stats_before_date("2022-05-01")

    @patch("premier_league.match_statistics.match_statistics.datetime")
    def test_update_data_set_current_season_august(
        self, mock_datetime, match_statistics
    ):
        """Test update_data_set sets correct season in August."""
        mock_now = MagicMock()
        mock_now.year = 2022
        mock_now.month = 8
        mock_datetime.now.return_value = mock_now

        with patch.object(match_statistics, "scrape_and_process_all") as mock_scrape:
            mock_scrape.return_value = []

            with patch.object(
                match_statistics, "_process_up_to_date_url"
            ) as mock_process:
                mock_process.return_value = []
                match_statistics.leagues = [
                    SimpleNamespace(
                        **{
                            "name": "Premier League",
                            "up_to_date_season": "2021-2022",
                            "match_weeks": 38,
                        }
                    ),
                ]
                match_statistics.update_data_set()
                assert match_statistics.current_season == "2022-2023"

    @patch("premier_league.match_statistics.match_statistics.datetime")
    def test_update_data_set_current_season_january(
        self, mock_datetime, match_statistics
    ):
        """Test update_data_set sets correct season in January."""
        mock_now = MagicMock()
        mock_now.year = 2022
        mock_now.month = 1
        mock_datetime.now.return_value = mock_now
        with patch.object(match_statistics, "scrape_and_process_all") as mock_scrape:
            mock_scrape.return_value = []

            with patch.object(
                match_statistics, "_process_up_to_date_url"
            ) as mock_process:
                mock_process.return_value = []
                match_statistics.leagues = [
                    SimpleNamespace(
                        **{
                            "name": "Premier League",
                            "up_to_date_season": "2021-2022",
                            "match_weeks": 38,
                        }
                    ),
                ]
                match_statistics.update_data_set()
                assert match_statistics.current_season == "2021-2022"

    def test_update_data_set_all_up_to_date(self, match_statistics):
        """Test update_data_set when all data is already up to date."""
        match_statistics.current_season = "2022-2023"
        with patch.object(match_statistics, "scrape_and_process_all") as mock_scrape:
            mock_scrape.return_value = ["page1"]

            with patch.object(
                match_statistics, "_process_up_to_date_url"
            ) as mock_process:
                mock_process.return_value = []
                with patch("builtins.print") as mock_print:
                    match_statistics.leagues = [
                        SimpleNamespace(
                            **{
                                "name": "Premier League",
                                "up_to_date_season": "2021-2022",
                                "match_weeks": 38,
                            }
                        ),
                    ]
                    match_statistics.update_data_set()
                    mock_print.assert_called_with("All Data is up to Date!")
                assert mock_scrape.call_count == 1
                assert mock_process.call_count == 1

    def test_process_up_to_date_url(self, match_statistics):
        """Test _process_up_to_date_url extracts correct URLs."""
        match_statistics.pages = [MagicMock(), MagicMock()]
        with patch.object(match_statistics, "process_xpath") as mock_process:
            mock_process.return_value = [
                "2021-2022 Premier League Scores",
                "2021-2022 La Liga Scores",
            ]
            match_statistics.leagues = [
                ("Premier League", "2021-2022", 38),
                ("La Liga", "2021-2022", 38),
            ]
            mock_page1 = match_statistics.pages[0]
            mock_page1.xpath.return_value = ["/matches/abc123/", "/matches/def456/"]

            mock_page2 = match_statistics.pages[1]
            mock_page2.xpath.return_value = ["/matches/ghi789/"]
            result = match_statistics._process_up_to_date_url()
            assert result == [
                "https://fbref.com/matches/abc123/",
                "https://fbref.com/matches/def456/",
                "https://fbref.com/matches/ghi789/",
            ]

    def test_wrap_result_with_url(self):
        """Test _wrap_result_with_url helper method."""
        result = MagicMock()
        url = "https://example.com"
        wrapped = MatchStatistics._wrap_result_with_url(result, url)
        assert wrapped == (result, url)
        wrapped = MatchStatistics._wrap_result_with_url(None, url)
        assert wrapped is None
