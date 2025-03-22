import json
from unittest.mock import patch

import pytest


@pytest.mark.usefixtures("client")
class TestPlayersRoutes:
    """Tests for the players routes."""

    @patch(
        "premier_league.api.services.player_service.PlayerService.get_player_data_goals"
    )
    def test_get_scorers(self, mock_get_goals, mock_player_goals_data, client):
        """Test GET /players/goals endpoint."""
        mock_get_goals.return_value = (mock_player_goals_data, 200)

        # Test without parameters
        response = client.get("/players/goals")
        assert response.status_code == 200
        assert json.loads(response.data) == mock_player_goals_data

        # Test with season parameter
        response = client.get("/players/goals?season=2022-2023")
        assert response.status_code == 200
        mock_get_goals.assert_called_with(
            season="2022-2023", limit=None, league="Premier League"
        )

        # Test with all parameters
        response = client.get(
            "/players/goals?season=2022-2023&limit=5&league=Premier league"
        )
        assert response.status_code == 200
        mock_get_goals.assert_called_with(
            season="2022-2023", limit=5, league="Premier league"
        )

        # Test invalid limit parameter
        response = client.get("/players/goals?limit=abc")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Limit must be a number"}

    @patch(
        "premier_league.api.services.player_service.PlayerService.get_player_data_assists"
    )
    def test_get_assists(self, mock_get_assists, mock_player_assists_data, client):
        """Test GET /players/assists endpoint."""
        mock_get_assists.return_value = (mock_player_assists_data, 200)

        # Test without parameters
        response = client.get("/players/assists")
        assert response.status_code == 200
        assert json.loads(response.data) == mock_player_assists_data

        # Test with parameters
        response = client.get("/players/assists?season=2022-2023&limit=10")
        assert response.status_code == 200
        mock_get_assists.assert_called_with(
            season="2022-2023", limit=10, league="Premier League"
        )

    @patch(
        "premier_league.api.services.player_service.PlayerService.get_player_data_goals_csv"
    )
    def test_get_scorers_csv(self, mock_get_csv, create_temp_file, client, tmp_path):
        """Test GET /players/goals/csv_file endpoint."""
        mock_get_csv.side_effect = lambda *args, **kwargs: (
            create_temp_file(
                "test_goals.csv",
                "name,team,goals\nHaaland,Man City,36\nKane,Spurs,30\n",
            ),
            200,
        )

        # Test with required parameters
        response = client.get("/players/goals/csv_file?filename=test_goals")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_goals.csv"
        )

        # Test without required filename
        response = client.get("/players/goals/csv_file")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Test without digit limit
        response = client.get("/players/goals/csv_file?limit=abc")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Limit must be a number"}

        # Test with all parameters
        response = client.get(
            "/players/goals/csv_file?filename=test_goals&season=2022-2023&limit=10&header=true&league=Premier league"
        )
        assert response.status_code == 200

        mock_get_csv.assert_called_with(
            file_name="test_goals",
            season="2022-2023",
            header="true",
            limit=10,
            league="Premier league",
        )

    @patch(
        "premier_league.api.services.player_service.PlayerService.get_player_data_assists_csv"
    )
    def test_get_assists_csv(self, mock_get_csv, create_temp_file, client, tmp_path):
        """Test GET /players/assists/csv_file endpoint."""
        mock_get_csv.side_effect = lambda *args, **kwargs: (
            create_temp_file(
                "test_assists.csv",
                "name,team,assists\nKevin De Bruyne,Manchester City,21\nMorgan Gibbs-White,Nottingham Forest,16\n",
            ),
            200,
        )

        # Test with required parameters
        response = client.get("/players/assists/csv_file?filename=test_assists")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_assists.csv"
        )

        # Test without required filename
        response = client.get("/players/assists/csv_file")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Test without digit limit
        response = client.get("/players/assists/csv_file?limit=abc")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Limit must be a number"}

        # Test with all parameters
        response = client.get(
            "/players/assists/csv_file?filename=test_assists&season=2005-2006&limit=26&header=false&league=Bundesliga"
        )
        assert response.status_code == 200

        mock_get_csv.assert_called_with(
            file_name="test_assists",
            season="2005-2006",
            header="false",
            limit=26,
            league="Bundesliga",
        )

    @patch(
        "premier_league.api.services.player_service.PlayerService.get_player_data_goals_json"
    )
    def test_get_scorers_json(
        self, mock_get_json, mock_player_goals_data, create_temp_file, client, tmp_path
    ):
        """Test GET /players/goals/json_file endpoint."""
        mock_get_json.side_effect = lambda *args, **kwargs: (
            create_temp_file("test_goals.json", str(mock_player_goals_data)),
            200,
        )

        # Test with required parameters
        response = client.get("/players/goals/json_file?filename=test_goals")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_goals.json"
        )

        # Test without required filename
        response = client.get("/players/goals/json_file")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Test with invalid limit
        response = client.get("/players/goals/json_file?filename=test_goals&limit=xyz")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Limit must be a number"}

        # Test with all parameters
        response = client.get(
            "/players/goals/json_file?filename=test_goals&season=2022-2023&limit=10&header=true&league=Premier league"
        )
        assert response.status_code == 200

        mock_get_json.assert_called_with(
            file_name="test_goals",
            season="2022-2023",
            header="true",
            limit=10,
            league="Premier league",
        )

    @patch(
        "premier_league.api.services.player_service.PlayerService.get_player_data_assists_json"
    )
    def test_get_assists_json(
        self,
        mock_get_json,
        mock_player_assists_data,
        create_temp_file,
        client,
        tmp_path,
    ):
        """Test GET /players/assists/json_file endpoint."""
        mock_get_json.side_effect = lambda *args, **kwargs: (
            create_temp_file("test_assists.json", str(mock_player_assists_data)),
            200,
        )

        # Test with required parameters
        response = client.get("/players/assists/json_file?filename=test_assists")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_assists.json"
        )

        # Test without required filename
        response = client.get("/players/assists/json_file")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Test with invalid limit
        response = client.get(
            "/players/assists/json_file?filename=test_assists&limit=xyz"
        )
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Limit must be a number"}

        # Test with all parameters
        response = client.get(
            "/players/assists/json_file?filename=test_assists&season=2022-2023&limit=10&header=true&league=Premier league"
        )
        assert response.status_code == 200

        mock_get_json.assert_called_with(
            file_name="test_assists",
            season="2022-2023",
            header="true",
            limit=10,
            league="Premier league",
        )
