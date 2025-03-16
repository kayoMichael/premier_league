import os
from unittest.mock import patch, MagicMock

from premier_league.api.services.transfer_service import TransferService


class TestTransferService:
    """Tests for the TransferService class."""

    @patch("premier_league.Transfers")
    def test_get_all_current_teams_success(self, mock_transfers_class):
        """Test successful retrieval of all teams."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.get_all_current_teams.return_value = [
            "Arsenal FC", "Chelsea FC", "Liverpool FC"
        ]
        result, status_code = TransferService.get_all_current_teams(league="Premier League", season="2022-2023")

        assert status_code == 200
        assert len(result) == 3
        assert result[0] == "Arsenal FC"

        mock_transfers_class.assert_called_once_with("2022-2023", "Premier League")
        mock_transfers_instance.get_all_current_teams.assert_called_once()

    @patch("premier_league.Transfers")
    def test_get_all_current_teams_error(self, mock_transfers_class):
        """Test error handling when retrieving all teams."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.get_all_current_teams.side_effect = ValueError("Invalid league")

        # Call service method
        result, status_code = TransferService.get_all_current_teams(league="Invalid League")

        # Assert results
        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid league"

    @patch("premier_league.api.services.transfer_service.export_to_dict")
    @patch("premier_league.Transfers")
    def test_get_transfer_in_data_success(self, mock_transfers_class, mock_export_to_dict):
        """Test successful retrieval of transfer-in data."""
        # Setup mocks
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfer_data = MagicMock()
        mock_transfers_instance.transfer_in_table.return_value = mock_transfer_data

        mock_export_to_dict.return_value = [
            {
                "Club": "São Paulo FC",
                "Date": "01/24",
                "Name": "Lucas Beraldo",
                "Position": "DF"
            },
            {
                "Club": "Eintracht Frankfurt",
                "Date": "09/23",
                "Name": "Randal Kolo Muani",
                "Position": "FW"
            }
        ]

        # Call service method
        result, status_code = TransferService.get_transfer_in_data(
            team="Arsenal",
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 200
        assert len(result) == 2
        assert result[0]["Name"] == "Lucas Beraldo"

        mock_transfers_class.assert_called_once_with("2022-2023", "Premier League")
        mock_transfers_instance.transfer_in_table.assert_called_once_with("Arsenal")
        mock_export_to_dict.assert_called_once_with(mock_transfer_data)

    @patch("premier_league.Transfers")
    def test_get_transfer_in_data_value_error(self, mock_transfers_class):
        """Test handling ValueError in get_transfer_in_data."""

        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_in_table.side_effect = ValueError("Invalid season")

        result, status_code = TransferService.get_transfer_in_data(
            team="Arsenal",
            league="Premier League",
            season="Invalid"
        )

        assert status_code == 400
        assert "error" in result
        assert result["error"] == "Invalid season"

    @patch("premier_league.Transfers")
    @patch("premier_league.TeamNotFoundError", Exception)
    def test_get_transfer_in_data_team_not_found(self, mock_transfers_class):
        """Test handling TeamNotFoundError in get_transfer_in_data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_in_table.side_effect = Exception(
            "Team not found")

        result, status_code = TransferService.get_transfer_in_data(
            team="NonexistentTeam",
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]

    @patch("premier_league.api.services.transfer_service.export_to_dict")
    @patch("premier_league.Transfers")
    def test_get_transfer_out_data_success(self, mock_transfers_class, mock_export_to_dict):
        """Test successful retrieval of transfer-out data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfer_data = MagicMock()
        mock_transfers_instance.transfer_out_table.return_value = mock_transfer_data

        mock_export_to_dict.return_value = [
            {"player": "Folarin Balogun", "from": "Arsenal", "to": "Monaco"}
        ]

        result, status_code = TransferService.get_transfer_out_data(
            team="Arsenal",
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 200
        assert len(result) == 1
        assert result[0]["player"] == "Folarin Balogun"

        mock_transfers_class.assert_called_once_with("2022-2023", "Premier League")
        mock_transfers_instance.transfer_out_table.assert_called_once_with("Arsenal")
        mock_export_to_dict.assert_called_once_with(mock_transfer_data)

    @patch("premier_league.transfers.transfers.TeamNotFoundError", Exception)
    @patch("premier_league.Transfers")
    def test_get_transfer_out_data_team_not_found(self, mock_transfers_class):
        """Test handling TeamNotFoundError in get_transfer_out_data."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_transfers_instance.transfer_out_table.side_effect = Exception(
            "Team not found")

        result, status_code = TransferService.get_transfer_out_data(
            team="NonexistentTeam",
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]

    @patch("os.path.join")
    @patch("premier_league.Transfers")
    def test_transfer_csv_success(self, mock_transfers_class, mock_path_join):
        """Test successful generation of CSV file."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_path_join.return_value = "/path/to/files/transfers.csv"

        result, status_code = TransferService.transfer_csv(
            team="Arsenal",
            file_name="transfers",
            transfer_type="both",
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 200
        assert result == "/path/to/files/transfers.csv"

        mock_transfers_class.assert_called_once_with("2022-2023", "Premier League")
        mock_transfers_instance.transfer_csv.assert_called_once_with("Arsenal", "transfers", "both")
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
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]

    @patch("os.path.join")
    @patch("premier_league.Transfers")
    def test_transfer_json_success(self, mock_transfers_class, mock_path_join):
        """Test successful generation of JSON file."""
        mock_transfers_instance = mock_transfers_class.return_value
        mock_path_join.return_value = "/path/to/files/transfers.json"

        result, status_code = TransferService.transfer_json(
            team="Arsenal",
            file_name="transfers",
            transfer_type="out",
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 200
        assert result == "/path/to/files/transfers.json"

        mock_transfers_class.assert_called_once_with("2022-2023", "Premier League")
        mock_transfers_instance.transfer_json.assert_called_once_with("Arsenal", "transfers", "out")
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
            league="Premier League",
            season="2022-2023"
        )

        assert status_code == 404
        assert "error" in result
        assert "No Team by the name of NonexistentTeam exists" in result["error"]