import os
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from premier_league.players.season_leaders import PlayerSeasonLeaders


class TestPlayerSeasonLeaders:
    """Tests for the PlayerSeasonLeaders class."""

    @staticmethod
    def base_init_side_effect(self, url, target_season, season_limit, cache):
        self.url = url
        self.target_season = target_season
        self.season_limit = season_limit
        self.cache = cache
        self.__post_init__()

    @patch("premier_league.players.season_leaders.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders._get_url")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders.request_url_page")
    @patch(
        "premier_league.players.season_leaders.PlayerSeasonLeaders._init_top_stats_table"
    )
    def test_init(
        self, mock_init_table, mock_request_page, mock_get_url, mock_base_init
    ):
        """Test the initialization of the PlayerSeasonLeaders class."""
        mock_get_url.return_value = (
            "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        mock_request_page.return_value = "<html>Mock Page</html>"
        mock_init_table.return_value = [["Header1", "Header2"], ["Value1", "Value2"]]
        mock_base_init.return_value = None

        # Mocks Parent Intialization of Url and Season
        mock_base_init.side_effect = self.base_init_side_effect

        player_leaders = PlayerSeasonLeaders(
            stat_type="G", target_season="2022-2023", league="Premier League"
        )

        # Verify attributes and method calls
        assert player_leaders.stat_type == "G"
        assert player_leaders.league == "Premier League"
        assert (
            player_leaders.stat_url
            == "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        assert player_leaders.page == "<html>Mock Page</html>"
        assert player_leaders._season_top_players_list == [
            ["Header1", "Header2"],
            ["Value1", "Value2"],
        ]
        assert player_leaders.season == "2022-2023"

        mock_get_url.assert_called_once()
        mock_request_page.assert_called_once()
        mock_init_table.assert_called_once()
        mock_base_init.side_effect = self.base_init_side_effect

        # Test with assists stat type
        mock_get_url.reset_mock()
        mock_base_init.reset_mock()
        player_leaders = PlayerSeasonLeaders(
            stat_type="A", target_season="2021-2022", league="La Liga"
        )

        assert player_leaders.stat_type == "A"
        assert player_leaders.league == "La Liga"
        assert player_leaders.season == "2021-2022"
        mock_get_url.assert_called_once()
        mock_base_init.assert_called_once()

    def test_get_url(self):
        # Test with valid stat type A
        player_leader = PlayerSeasonLeaders(
            stat_type="A", target_season="2021-2022", league="La Liga"
        )
        player_leader.url = (
            "https://www.worldfootball.net/assists/esp-primera-division-2021-2022/"
        )

        # Test with valid stat type G
        player_leader = PlayerSeasonLeaders(
            stat_type="G", target_season="1999-2000", league="Bundesliga"
        )
        player_leader.url = "https://www.worldfootball.net/goals/bundesliga-1999-2000/"

        # Test with Invalid Stat Type
        with pytest.raises(ValueError) as exc_info:
            PlayerSeasonLeaders(
                stat_type="X", target_season="2021-2022", league="La Liga"
            )
        assert str(exc_info.value) == "Type X not found. The Available Types are: G, A"

    @patch("premier_league.players.season_leaders.BaseScrapper.__init__")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders._get_url")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders.request_url_page")
    @patch(
        "premier_league.players.season_leaders.PlayerSeasonLeaders.get_list_by_xpath"
    )
    def test_init_top_stats_table_goals(
        self, mock_get_list, mock_request_page, mock_get_url, mock_base_init
    ):
        """Test the _init_top_stats_table method for goals."""
        mock_base_init.return_value = None
        mock_get_url.return_value = (
            "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        mock_request_page.return_value = "<html>Mock Page</html>"
        mock_get_list.return_value = [
            "1.",
            "Mohamed Salah",
            "Egypt",
            "Liverpool",
            "19",
            "14+5",
            "2.",
            "Erling Haaland",
            "Norway",
            "Manchester City",
            "27",
            "23+4",
            "3.",
            "Ivan Toney",
            "England",
            "Brentford",
            "20",
            "16+4",
        ]

        # Create instance and call _init_top_stats_table
        player_leaders = PlayerSeasonLeaders(stat_type="G", league="Premier League")
        result = player_leaders._init_top_stats_table()

        expected = [
            ["Name", "Country", "Club", "Goals", "In Play Goals+Penalty"],
            ["Mohamed Salah", "Egypt", "Liverpool", "19", "14+5"],
            ["Erling Haaland", "Norway", "Manchester City", "27", "23+4"],
            ["Ivan Toney", "England", "Brentford", "20", "16+4"],
        ]
        assert result == expected

    @patch("premier_league.players.season_leaders.BaseScrapper.__init__")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders._get_url")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders.request_url_page")
    @patch(
        "premier_league.players.season_leaders.PlayerSeasonLeaders.get_list_by_xpath"
    )
    def test_init_top_stats_table_assists(
        self, mock_get_list, mock_request_page, mock_get_url, mock_base_init
    ):
        """Test the _init_top_stats_table method for assists."""
        # Set up mocks for assists stats
        mock_base_init.return_value = None
        mock_get_url.return_value = (
            "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        mock_request_page.return_value = "<html>Mock Page</html>"
        mock_get_list.return_value = [
            "1.",
            "Kevin De Bruyne",
            "Belgium",
            "Manchester City",
            "16",
            "2.",
            "Leandro Trossard",
            "Belgium",
            "Arsenal",
            "12",
            "3.",
            "Mohamed Salah",
            "Egypt",
            "Liverpool",
            "12",
        ]

        # Create instance and call _init_top_stats_table
        player_leaders = PlayerSeasonLeaders(stat_type="A", league="Premier League")
        result = player_leaders._init_top_stats_table()

        expected = [
            ["Name", "Country", "Club", "Assists"],
            ["Kevin De Bruyne", "Belgium", "Manchester City", "16"],
            ["Leandro Trossard", "Belgium", "Arsenal", "12"],
            ["Mohamed Salah", "Egypt", "Liverpool", "12"],
        ]
        assert result == expected

    @patch("premier_league.players.season_leaders.BaseScrapper.__init__")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders._get_url")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders.request_url_page")
    def test_get_top_stats_list(self, mock_request_page, mock_get_url, mock_base_init):
        """Test the get_top_stats_list method."""
        mock_base_init.return_value = None
        mock_get_url.return_value = (
            "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        mock_request_page.return_value = "<html>Mock Page</html>"

        # Create instance with mocked _init_top_stats_table
        with patch.object(
            PlayerSeasonLeaders, "_init_top_stats_table"
        ) as mock_init_table:
            mock_player_data = [
                ["Name", "Country", "Club", "Goals", "In Play Goals+Penalty"],
                ["Player1", "Country1", "Club1", "25", "20+5"],
                ["Player2", "Country2", "Club2", "20", "18+2"],
                ["Player3", "Country3", "Club3", "15", "13+2"],
                ["Player4", "Country4", "Club4", "10", "8+2"],
            ]
            mock_init_table.return_value = mock_player_data

            player_leaders = PlayerSeasonLeaders(stat_type="G", league="Premier League")

            # Test without limit
            result = player_leaders.get_top_stats_list()
            assert result == mock_player_data

            # Test with limit
            result = player_leaders.get_top_stats_list(limit=2)
            assert result == mock_player_data[:3]  # header + 2 players

    @patch("premier_league.players.season_leaders.export_to_csv")
    @patch("premier_league.players.season_leaders.BaseScrapper.__init__")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders._get_url")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders.request_url_page")
    def test_get_top_stats_csv(
        self, mock_request_page, mock_get_url, mock_base_init, mock_export_csv
    ):
        """Test the get_top_stats_csv method."""
        # Set up mocks
        mock_base_init.return_value = None
        mock_get_url.return_value = (
            "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        mock_request_page.return_value = "<html>Mock Page</html>"

        # Create instance with mocked _init_top_stats_table and get_top_stats_list
        with patch.object(
            PlayerSeasonLeaders, "_init_top_stats_table"
        ) as mock_init_table:
            mock_player_data = [
                ["Name", "Country", "Club", "Goals", "In Play Goals+Penalty"],
                ["Player1", "Country1", "Club1", "25", "20+5"],
            ]
            mock_init_table.return_value = mock_player_data

            player_leaders = PlayerSeasonLeaders(stat_type="G", league="Premier League")

            # Test CSV export
            player_leaders.get_top_stats_csv(
                file_name="test_file", header="Test Header", limit=5
            )
            mock_export_csv.assert_called_once_with(
                "test_file", mock_player_data, "Test Header"
            )

    @patch("premier_league.players.season_leaders.export_to_json")
    @patch("premier_league.players.season_leaders.BaseScrapper.__init__")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders._get_url")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders.request_url_page")
    def test_get_top_stats_json(
        self, mock_request_page, mock_get_url, mock_base_init, mock_export_json
    ):
        """Test the get_top_stats_json method."""
        # Set up mocks
        mock_base_init.return_value = None
        mock_get_url.return_value = (
            "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        mock_request_page.return_value = "<html>Mock Page</html>"

        # Create instance with mocked _init_top_stats_table and get_top_stats_list
        with patch.object(
            PlayerSeasonLeaders, "_init_top_stats_table"
        ) as mock_init_table:
            mock_player_data = [
                ["Name", "Country", "Club", "Assists"],
                ["Player1", "Country1", "Club1", "15"],
            ]
            mock_init_table.return_value = mock_player_data

            player_leaders = PlayerSeasonLeaders(stat_type="A", league="Premier League")

            # Test JSON export
            player_leaders.get_top_stats_json(
                file_name="test_file", header="Test Header", limit=5
            )
            mock_export_json.assert_called_once_with(
                "test_file", mock_player_data, header_1="Test Header"
            )

    @patch("reportlab.pdfgen.canvas.Canvas")
    @patch("reportlab.platypus.Table")
    @patch("premier_league.players.season_leaders.BaseScrapper.__init__")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders._get_url")
    @patch("premier_league.players.season_leaders.PlayerSeasonLeaders.request_url_page")
    def test_get_top_stats_pdf(
        self,
        mock_request_page,
        mock_get_url,
        mock_base_init,
        mock_table,
        mock_canvas,
    ):
        """Test the get_top_stats_pdf method."""
        mock_base_init.return_value = None
        mock_get_url.return_value = (
            "https://www.worldfootball.net/goals/eng-premier-league-2022-2023/"
        )
        mock_request_page.return_value = "<html>Mock Page</html>"
        mock_pdf = MagicMock()
        mock_canvas.return_value = mock_pdf
        mock_table_instance = MagicMock()
        mock_table_instance.wrapOn.return_value = (571.921875, 792)
        mock_table.return_value = mock_table_instance

        with patch.object(
            PlayerSeasonLeaders, "_init_top_stats_table"
        ) as mock_init_table:
            mock_player_data = [
                ["Name", "Country", "Club", "Goals", "In Play Goals+Penalty"],
                ["Player1", "Country1", "Club1", "25", "20+5"],
            ]
            mock_init_table.return_value = mock_player_data

            # Mock the season property BEFORE creating the instance
            with patch.object(
                PlayerSeasonLeaders, "season", new_callable=PropertyMock
            ) as mock_season:
                mock_season.return_value = "2022-2023"

                player_leaders = PlayerSeasonLeaders(
                    stat_type="G", league="Premier League"
                )

                player_leaders.get_top_stats_pdf(file_name="test_file", path="test")
                mock_canvas.assert_called_once()
                mock_table.assert_called_once_with(mock_player_data[:22])
                mock_table_instance.setStyle.assert_called_once()
                mock_pdf.save.assert_called_once()
                if os.path.exists("test") and not os.listdir("test"):
                    os.rmdir("test")
