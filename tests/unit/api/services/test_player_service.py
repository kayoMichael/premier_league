import os
from unittest.mock import MagicMock, patch

from premier_league.api.services.player_service import PlayerService


class TestPlayerService:
    """Tests for the PlayerService class."""

    @patch("premier_league.api.services.player_service.export_to_dict")
    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_goals_success(
        self, mock_player_leaders_class, mock_export_to_dict, mock_player_goals_data
    ):
        """Test successful retrieval of goal scoring data."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_data = MagicMock()
        mock_player_leaders_instance.get_top_stats_list.return_value = mock_player_data

        mock_export_to_dict.return_value = mock_player_goals_data

        result, status_code = PlayerService.get_player_data_goals(
            league="Premier League", season="2022-2023", limit=10
        )

        assert status_code == 200
        assert result == mock_player_goals_data

        mock_player_leaders_class.assert_called_once_with(
            "G", "2022-2023", "Premier League"
        )
        mock_player_leaders_instance.get_top_stats_list.assert_called_once_with(
            limit=10
        )
        mock_export_to_dict.assert_called_once_with(mock_player_data)

    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_goals_error(self, mock_player_leaders_class):
        """Test error handling when retrieving goal scoring data."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_leaders_instance.get_top_stats_list.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = PlayerService.get_player_data_goals(
            league="Invalid League", season="2022-2023"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("premier_league.api.services.player_service.export_to_dict")
    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_assists_success(
        self, mock_player_leaders_class, mock_export_to_dict, mock_player_assists_data
    ):
        """Test successful retrieval of assist data."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_data = MagicMock()
        mock_player_leaders_instance.get_top_stats_list.return_value = mock_player_data

        mock_export_to_dict.return_value = mock_player_assists_data

        result, status_code = PlayerService.get_player_data_assists(
            league="Premier League", season="2022-2023", limit=5
        )

        assert status_code == 200
        assert result == mock_player_assists_data

        mock_player_leaders_class.assert_called_once_with(
            "A", "2022-2023", "Premier League"
        )
        mock_player_leaders_instance.get_top_stats_list.assert_called_once_with(limit=5)
        mock_export_to_dict.assert_called_once_with(mock_player_data)

    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_assists_error(self, mock_player_leaders_class):
        """Test error handling when retrieving assist data."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_leaders_instance.get_top_stats_list.side_effect = ValueError(
            "Invalid season"
        )

        result, status_code = PlayerService.get_player_data_assists(
            league="Premier League", season="Invalid"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid season"

    @patch("os.path.join")
    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_goals_csv_success(
        self, mock_player_leaders_class, mock_path_join
    ):
        """Test successful generation of goals CSV file."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_path_join.return_value = "/path/to/files/top_scorers.csv"

        result, status_code = PlayerService.get_player_data_goals_csv(
            file_name="top_scorers",
            league="Premier League",
            season="2022-2023",
            header="Top Scorers",
            limit=10,
        )

        assert status_code == 200
        assert result == "/path/to/files/top_scorers.csv"

        mock_player_leaders_class.assert_called_once_with(
            "G", "2022-2023", "Premier League"
        )
        mock_player_leaders_instance.get_top_stats_csv.assert_called_once_with(
            "top_scorers", "Top Scorers", 10
        )
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "top_scorers.csv")

    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_goals_csv_error(self, mock_player_leaders_class):
        """Test error handling when generating goals CSV file."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_leaders_instance.get_top_stats_csv.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = PlayerService.get_player_data_goals_csv(
            file_name="top_scorers", league="Invalid League", season="2022-2023"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("os.path.join")
    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_assists_csv_success(
        self, mock_player_leaders_class, mock_path_join
    ):
        """Test successful generation of assists CSV file."""
        # Setup mocks
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_path_join.return_value = "/path/to/files/top_assists.csv"

        # Call service method
        result, status_code = PlayerService.get_player_data_assists_csv(
            file_name="top_assists",
            league="Premier League",
            season="2022-2023",
            header="Top Playmakers",
            limit=10,
        )

        # Assert results
        assert status_code == 200
        assert result == "/path/to/files/top_assists.csv"

        # Verify mocks were called with correct parameters
        mock_player_leaders_class.assert_called_once_with(
            "A", "2022-2023", "Premier League"
        )
        mock_player_leaders_instance.get_top_stats_csv.assert_called_once_with(
            "top_assists", "Top Playmakers", 10
        )
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "top_assists.csv")

    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_assists_csv_error(self, mock_player_leaders_class):
        """Test error handling when generating assists CSV file."""
        # Setup mock to raise ValueError
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_leaders_instance.get_top_stats_csv.side_effect = ValueError(
            "Invalid league"
        )

        # Call service method
        result, status_code = PlayerService.get_player_data_assists_csv(
            file_name="top_assists", league="Invalid League", season="2022-2023"
        )

        # Assert results
        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("os.path.join")
    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_goals_json_success(
        self, mock_player_leaders_class, mock_path_join
    ):
        """Test successful generation of goals JSON file."""
        # Setup mocks
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_path_join.return_value = "/path/to/files/top_scorers.json"

        # Call service method
        result, status_code = PlayerService.get_player_data_goals_json(
            file_name="top_scorers",
            league="Premier League",
            season="2022-2023",
            header="Top Scorers",
            limit=10,
        )

        # Assert results
        assert status_code == 200
        assert result == "/path/to/files/top_scorers.json"

        # Verify mocks were called with correct parameters
        mock_player_leaders_class.assert_called_once_with(
            "G", "2022-2023", "Premier League"
        )
        mock_player_leaders_instance.get_top_stats_json.assert_called_once_with(
            "top_scorers", "Top Scorers", 10
        )
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "top_scorers.json")

    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_goals_json_error(self, mock_player_leaders_class):
        """Test error handling when generating goals JSON file."""
        # Setup mock to raise ValueError
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_leaders_instance.get_top_stats_json.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = PlayerService.get_player_data_goals_json(
            file_name="top_scorers", league="Invalid League", season="2022-2023"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("os.path.join")
    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_assists_json_success(
        self, mock_player_leaders_class, mock_path_join
    ):
        """Test successful generation of assists JSON file."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_path_join.return_value = "/path/to/files/top_assists.json"

        result, status_code = PlayerService.get_player_data_assists_json(
            file_name="top_assists",
            league="Premier League",
            season="2022-2023",
            header="Top Playmakers",
            limit=10,
        )

        assert status_code == 200
        assert result == "/path/to/files/top_assists.json"

        mock_player_leaders_class.assert_called_once_with(
            "A", "2022-2023", "Premier League"
        )
        mock_player_leaders_instance.get_top_stats_json.assert_called_once_with(
            "top_assists", "Top Playmakers", 10
        )
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "top_assists.json")

    @patch("premier_league.PlayerSeasonLeaders")
    def test_get_player_data_assists_json_error(self, mock_player_leaders_class):
        """Test error handling when generating assists JSON file."""
        mock_player_leaders_instance = mock_player_leaders_class.return_value
        mock_player_leaders_instance.get_top_stats_json.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = PlayerService.get_player_data_assists_json(
            file_name="top_assists", league="Invalid League", season="2022-2023"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"
