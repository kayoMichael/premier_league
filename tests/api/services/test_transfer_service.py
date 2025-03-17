import os
from unittest.mock import MagicMock, patch

from premier_league.api.services.transfer_service import TransferService


class TestTransferService:
    """Tests for the TransferService class."""

    @patch("premier_league.Transfers")
    def test_get_all_current_teams_success(self, mock_transfers_class, mock_teams_data):
        """Test successful retrieval of all teams."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.get_all_current_teams.return_value = mock_teams_data

        # Call service method
        result, status_code = TransferService.get_all_current_teams(
            league="Premier League", season="2022-2023"
        )

        # Assert results
        assert status_code == 200
        assert len(result) == 4
        assert result[0] == "Arsenal FC"

        # Verify mock was called with correct parameters
        mock_transfers_class.assert_called_once_with("2022-2023", "Premier League")
        mock_transfers_instance.get_all_current_teams.assert_called_once()

    @patch("premier_league.Transfers")
    def test_get_all_current_teams_error(self, mock_transfers_class):
        """Test error handling when retrieving all teams."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.get_all_current_teams.side_effect = ValueError(
            "Invalid league"
        )

        result, status_code = TransferService.get_all_current_teams(
            league="Invalid League"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("premier_league.api.services.transfer_service.export_to_dict")
    @patch("premier_league.Transfers")
    def test_get_transfer_in_data_success(
        self, mock_transfers_class, mock_export_to_dict, mock_transfer_data
    ):
        """Test successful retrieval of transfer-in data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfer_table = MagicMock()
        mock_transfers_instance.transfer_in_table.return_value = mock_transfer_table

        mock_export_to_dict.return_value = mock_transfer_data

        result, status_code = TransferService.get_transfer_in_data(
            team="Paris Saint-Germain", league="Ligue 1", season="2023-2024"
        )

        assert status_code == 200
        assert result == mock_transfer_data

        mock_transfers_class.assert_called_once_with("2023-2024", "Ligue 1")
        mock_transfers_instance.transfer_in_table.assert_called_once_with(
            "Paris Saint-Germain"
        )
        mock_export_to_dict.assert_called_once_with(mock_transfer_table)

    @patch("premier_league.Transfers")
    def test_get_transfer_in_data_value_error(self, mock_transfers_class):
        """Test handling ValueError in get_transfer_in_data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_in_table.side_effect = ValueError(
            "Invalid season"
        )

        result, status_code = TransferService.get_transfer_in_data(
            team="PSG", league="Ligue 1", season="Invalid"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid season"

    @patch("premier_league.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_get_transfer_in_data_team_not_found(self, mock_transfers_class):
        """Test handling TeamNotFoundError in get_transfer_in_data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_in_table.side_effect = Exception(
            "Team not found"
        )

        result, status_code = TransferService.get_transfer_in_data(
            team="NonexistentTeam", league="Ligue 1", season="2023-2024"
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]

    @patch("premier_league.api.services.transfer_service.export_to_dict")
    @patch("premier_league.transfers.transfers.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_get_transfer_out_data_success(
        self, mock_transfers_class, mock_export_to_dict, mock_transfer_data
    ):
        """Test successful retrieval of transfer-out data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfer_table = MagicMock()
        mock_transfers_instance.transfer_out_table.return_value = mock_transfer_table

        mock_export_to_dict.return_value = mock_transfer_data

        result, status_code = TransferService.get_transfer_out_data(
            team="Paris Saint-Germain", league="Ligue 1", season="2023-2024"
        )

        assert status_code == 200
        assert result == mock_transfer_data

        mock_transfers_class.assert_called_once_with("2023-2024", "Ligue 1")
        mock_transfers_instance.transfer_out_table.assert_called_once_with(
            "Paris Saint-Germain"
        )
        mock_export_to_dict.assert_called_once_with(mock_transfer_table)

    @patch("premier_league.transfers.transfers.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_get_transfer_out_data_team_not_found(self, mock_transfers_class):
        """Test handling TeamNotFoundError in get_transfer_out_data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_out_table.side_effect = Exception(
            "Team not found"
        )

        result, status_code = TransferService.get_transfer_out_data(
            team="NonexistentTeam", league="Ligue 1", season="2023-2024"
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]

    @patch("os.path.join")
    @patch("premier_league.transfers.transfers.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_transfer_csv_success(self, mock_transfers_class, mock_path_join):
        """Test successful generation of CSV file."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_path_join.return_value = "/path/to/files/transfers.csv"

        result, status_code = TransferService.transfer_csv(
            team="PSG",
            file_name="transfers",
            transfer_type="both",
            league="Ligue 1",
            season="2023-2024",
        )

        assert status_code == 200
        assert result == "/path/to/files/transfers.csv"

        mock_transfers_class.assert_called_once_with("2023-2024", "Ligue 1")
        mock_transfers_instance.transfer_csv.assert_called_once_with(
            "PSG", "transfers", "both"
        )
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "transfers.csv")

    @patch("premier_league.transfers.transfers.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_transfer_csv_team_not_found(self, mock_transfers_class):
        """Test handling TeamNotFoundError in transfer_csv."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_csv.side_effect = Exception("Team not found")

        result, status_code = TransferService.transfer_csv(
            team="NonexistentTeam",
            file_name="transfers",
            transfer_type="in",
            league="Ligue 1",
            season="2023-2024",
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]

    @patch("os.path.join")
    @patch("premier_league.transfers.transfers.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_transfer_json_success(self, mock_transfers_class, mock_path_join):
        """Test successful generation of JSON file."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_path_join.return_value = "/path/to/files/transfers.json"

        result, status_code = TransferService.transfer_json(
            team="PSG",
            file_name="transfers",
            transfer_type="out",
            league="Ligue 1",
            season="2023-2024",
        )

        assert status_code == 200
        assert result == "/path/to/files/transfers.json"

        mock_transfers_class.assert_called_once_with("2023-2024", "Ligue 1")
        mock_transfers_instance.transfer_json.assert_called_once_with(
            "PSG", "transfers", "out"
        )
        mock_path_join.assert_called_once_with(os.getcwd(), "files", "transfers.json")

    @patch("premier_league.transfers.transfers.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_transfer_json_team_not_found(self, mock_transfers_class):
        """Test handling TeamNotFoundError in transfer_json."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_json.side_effect = Exception("Team not found")

        result, status_code = TransferService.transfer_json(
            team="NonexistentTeam",
            file_name="transfers",
            transfer_type="both",
            league="Ligue 1",
            season="2023-2024",
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]
