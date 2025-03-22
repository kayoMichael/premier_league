import json
from unittest.mock import patch

import pytest


@pytest.mark.usefixtures("client")
class TestTransferRoutes:
    """Tests for the transfer routes."""

    @patch(
        "premier_league.api.services.transfer_service.TransferService.get_all_current_teams"
    )
    def test_get_all_teams(self, mock_get_all_teams, mock_teams_data, client):
        """Test GET /all_teams endpoint."""
        mock_get_all_teams.return_value = (mock_teams_data, 200)

        # Test without parameters
        response = client.get("/all_teams")
        assert response.status_code == 200
        assert json.loads(response.data) == mock_teams_data
        mock_get_all_teams.assert_called_with(league=None, season=None)

        # Test with season parameter
        response = client.get("/all_teams?season=2022-2023")
        assert response.status_code == 200
        mock_get_all_teams.assert_called_with(league=None, season="2022-2023")

        # Test with all parameters
        response = client.get("/all_teams?season=2022-2023&league=La Liga")
        assert response.status_code == 200
        mock_get_all_teams.assert_called_with(league="La Liga", season="2022-2023")

    @patch(
        "premier_league.api.services.transfer_service.TransferService.get_transfer_in_data"
    )
    def test_get_transfer_in_data(
        self, mock_get_transfer_in, mock_transfer_data, client
    ):
        """Test GET /transfers/in endpoint."""
        mock_get_transfer_in.return_value = (mock_transfer_data, 200)

        # Missing required parameter
        response = client.get("/transfers/in")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing team parameter"}

        # Test with required parameters
        response = client.get("/transfers/in?team=Arsenal")
        assert response.status_code == 200
        assert json.loads(response.data) == mock_transfer_data
        mock_get_transfer_in.assert_called_with(
            team="Arsenal", season=None, league="Premier League"
        )

        # Test with all parameters
        response = client.get(
            "/transfers/in?team=Barcelona&season=2022-2023&league=La Liga"
        )
        assert response.status_code == 200
        mock_get_transfer_in.assert_called_with(
            team="Barcelona", season="2022-2023", league="La Liga"
        )

    @patch(
        "premier_league.api.services.transfer_service.TransferService.get_transfer_out_data"
    )
    def test_get_transfer_out_data(
        self, mock_get_transfer_out, mock_transfer_data, client
    ):
        """Test GET /transfers/out endpoint."""
        mock_get_transfer_out.return_value = (mock_transfer_data, 200)

        # Missing required parameter
        response = client.get("/transfers/out")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing team parameter"}

        # Test with required parameters
        response = client.get("/transfers/out?team=Arsenal")
        assert response.status_code == 200
        assert json.loads(response.data) == mock_transfer_data
        mock_get_transfer_out.assert_called_with(
            team="Arsenal", season=None, league="Premier League"
        )

        # Test with all parameters
        response = client.get(
            "/transfers/out?team=Barcelona&season=2022-2023&league=La Liga"
        )
        assert response.status_code == 200
        mock_get_transfer_out.assert_called_with(
            team="Barcelona", season="2022-2023", league="La Liga"
        )

    @patch("premier_league.api.services.transfer_service.TransferService.transfer_csv")
    def test_get_transfer_data_csv(
        self, mock_transfer_csv, create_temp_file, client, tmp_path
    ):
        """Test GET /transfers/csv_file endpoint."""
        mock_transfer_csv.side_effect = lambda *args, **kwargs: (
            create_temp_file(
                "test_transfers.csv",
                "Player,From,To,Fee\nMartin Odegaard,Real Madrid,Arsenal,£30m",
            ),
            200,
        )

        # Missing team parameter
        response = client.get("/transfers/csv_file?filename=test_transfers")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing team parameter"}

        # Missing filename parameter
        response = client.get("/transfers/csv_file?team=Arsenal")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Invalid transfer_type parameter
        response = client.get(
            "/transfers/csv_file?team=Arsenal&filename=test_transfers&transfer_type=invalid"
        )
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Invalid type parameter"}

        # Test with required parameters (default transfer_type)
        response = client.get(
            "/transfers/csv_file?team=Arsenal&filename=test_transfers"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_transfers.csv"
        )
        mock_transfer_csv.assert_called_with(
            team="Arsenal",
            file_name="test_transfers",
            transfer_type="both",
            season=None,
            league="Premier League",
        )

        # Test with all parameters
        response = client.get(
            "/transfers/csv_file?team=Barcelona&filename=test_transfers&season=2022-2023&league=La Liga&transfer_type=in"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_transfers.csv"
        )
        mock_transfer_csv.assert_called_with(
            team="Barcelona",
            file_name="test_transfers",
            transfer_type="in",
            season="2022-2023",
            league="La Liga",
        )

    @patch("premier_league.api.services.transfer_service.TransferService.transfer_json")
    def test_get_transfer_data_json(
        self, mock_transfer_json, create_temp_file, client, tmp_path
    ):
        """Test GET /transfers/json_file endpoint."""
        mock_transfer_json.side_effect = lambda *args, **kwargs: (
            create_temp_file(
                "test_transfers.json",
                '{"transfers": [{"Player": "Martin Odegaard", "From": "Real Madrid", "To": "Arsenal", "Fee": "£30m"}]}',
            ),
            200,
        )

        # Missing team parameter
        response = client.get("/transfers/json_file?filename=test_transfers")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing team parameter"}

        # Missing filename parameter
        response = client.get("/transfers/json_file?team=Arsenal")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Invalid transfer_type parameter
        response = client.get(
            "/transfers/json_file?team=Arsenal&filename=test_transfers&transfer_type=invalid"
        )
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Invalid type parameter"}

        # Test with required parameters (default transfer_type)
        response = client.get(
            "/transfers/json_file?team=Arsenal&filename=test_transfers"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_transfers.json"
        )
        mock_transfer_json.assert_called_with(
            team="Arsenal",
            file_name="test_transfers",
            transfer_type="both",
            season=None,
            league="Premier League",
        )

        # Test with all parameters
        response = client.get(
            "/transfers/json_file?team=Barcelona&filename=test_transfers&season=2022-2023&league=La Liga&transfer_type=out"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_transfers.json"
        )
        mock_transfer_json.assert_called_with(
            team="Barcelona",
            file_name="test_transfers",
            transfer_type="out",
            season="2022-2023",
            league="La Liga",
        )
