import os
from unittest.mock import MagicMock, patch

import pytest

from premier_league.api.services.ranking_service import RankingService


class TestRankingService:
    """Tests for the RankingService class."""

    @patch("premier_league.RankingTable")
    def test_get_ranking_success(self, mock_ranking_table_class, mock_ranking_data):
        """Test successful retrieval of ranking data."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_ranking_table_instance.get_ranking_dict.return_value = mock_ranking_data

        result, status_code = RankingService.get_ranking(
            season="2022-2023", header="Stats", league="Premier League"
        )

        assert status_code == 200
        assert result == mock_ranking_data

        mock_ranking_table_class.assert_called_once_with("Premier League", "2022-2023")
        mock_ranking_table_instance.get_ranking_dict.assert_called_once_with("Stats")

    @patch("premier_league.RankingTable")
    def test_get_ranking_error(self, mock_ranking_table_class):
        """Test error handling when retrieving ranking data."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_ranking_table_instance.get_ranking_dict.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = RankingService.get_ranking(league="Invalid League")

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("premier_league.RankingTable")
    def test_get_ranking_list_success(
        self, mock_ranking_table_class, mock_ranking_data_list
    ):
        """Test successful retrieval of ranking list data."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_ranking_table_instance.get_ranking_list.return_value = (
            mock_ranking_data_list
        )

        result, status_code = RankingService.get_ranking_list(
            season="2022-2023", league="Premier League"
        )

        assert status_code == 200
        assert result == mock_ranking_data_list

        mock_ranking_table_class.assert_called_once_with("Premier League", "2022-2023")
        mock_ranking_table_instance.get_ranking_list.assert_called_once()

    @patch("premier_league.RankingTable")
    def test_get_ranking_list_error(self, mock_ranking_table_class):
        """Test error handling when retrieving ranking list data."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_ranking_table_instance.get_ranking_list.side_effect = ValueError(
            "Invalid season"
        )

        result, status_code = RankingService.get_ranking_list(
            season="Invalid", league="Premier League"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid season"

    @patch("os.path.join")
    @patch("premier_league.RankingTable")
    def test_get_ranking_csv_success(self, mock_ranking_table_class, mock_path_join):
        """Test successful generation of CSV file."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_path_join.return_value = "/path/to/files/ranking.csv"

        result, status_code = RankingService.get_ranking_csv(
            file_name="ranking", season="2022-2023", league="Premier League"
        )
        assert status_code == 200
        assert result == "/path/to/files/ranking.csv"

        mock_ranking_table_class.assert_called_once_with("Premier League", "2022-2023")
        mock_ranking_table_instance.get_ranking_csv.assert_called_once_with("ranking")
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "ranking.csv")

    @patch("premier_league.RankingTable")
    def test_get_ranking_csv_error(self, mock_ranking_table_class):
        """Test error handling when generating CSV file."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_ranking_table_instance.get_ranking_csv.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = RankingService.get_ranking_csv(
            file_name="ranking", league="Invalid League"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("os.path.join")
    @patch("premier_league.RankingTable")
    def test_get_ranking_json_success(self, mock_ranking_table_class, mock_path_join):
        """Test successful generation of JSON file."""
        # Setup mocks
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_path_join.return_value = "/path/to/files/ranking.json"

        result, status_code = RankingService.get_ranking_json(
            file_name="ranking", season="2022-2023", league="Premier League"
        )

        assert status_code == 200
        assert result == "/path/to/files/ranking.json"

        mock_ranking_table_class.assert_called_once_with("Premier League", "2022-2023")
        mock_ranking_table_instance.get_ranking_json.assert_called_once_with("ranking")
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "ranking.json")

    @patch("premier_league.RankingTable")
    def test_get_ranking_json_error(self, mock_ranking_table_class):
        """Test error handling when generating JSON file."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_ranking_table_instance.get_ranking_json.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = RankingService.get_ranking_json(
            file_name="ranking", league="Invalid League"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("os.path.join")
    @patch("premier_league.RankingTable")
    def test_get_ranking_pdf_success(self, mock_ranking_table_class, mock_path_join):
        """Test successful generation of PDF file."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_path_join.return_value = "/path/to/files/ranking.pdf"

        result, status_code = RankingService.get_ranking_pdf(
            file_name="ranking", season="2022-2023", league="Premier League"
        )

        assert status_code == 200
        assert result == "/path/to/files/ranking.pdf"

        mock_ranking_table_class.assert_called_once_with("Premier League", "2022-2023")
        mock_ranking_table_instance.get_ranking_pdf.assert_called_once_with("ranking")
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "ranking.pdf")

    @patch("premier_league.RankingTable")
    def test_get_ranking_pdf_error(self, mock_ranking_table_class):
        """Test error handling when generating PDF file."""
        mock_ranking_table_instance = mock_ranking_table_class.return_value
        mock_ranking_table_instance.get_ranking_pdf.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = RankingService.get_ranking_pdf(
            file_name="ranking", league="Invalid League"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"
