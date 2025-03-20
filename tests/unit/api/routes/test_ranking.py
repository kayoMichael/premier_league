import json
from unittest.mock import patch

import pytest


@pytest.mark.usefixtures("client")
class TestRankingRoutes:
    """Tests for the ranking routes."""

    @patch("premier_league.api.services.ranking_service.RankingService.get_ranking")
    def test_get_standings(self, mock_get_ranking, mock_ranking_data, client):
        """Test GET /ranking endpoint."""
        mock_get_ranking.return_value = (mock_ranking_data, 200)

        # Test without parameters
        response = client.get("/ranking")
        assert response.status_code == 200
        assert json.loads(response.data) == mock_ranking_data
        mock_get_ranking.assert_called_with(
            season=None, league="Premier League", header=None
        )

        # Test with season parameter
        response = client.get("/ranking?season=2022-2023")
        assert response.status_code == 200
        mock_get_ranking.assert_called_with(
            season="2022-2023", league="Premier League", header=None
        )

        # Test with all parameters
        response = client.get(
            "/ranking?season=2001-2002&league=La Liga&header=Estadísticas"
        )
        assert response.status_code == 200
        mock_get_ranking.assert_called_with(
            season="2001-2002", league="La Liga", header="Estadísticas"
        )

    @patch(
        "premier_league.api.services.ranking_service.RankingService.get_ranking_list"
    )
    def test_get_standings_list(
        self, mock_get_ranking_list, mock_ranking_data_list, client
    ):
        """Test GET /ranking/table endpoint."""
        mock_get_ranking_list.return_value = (mock_ranking_data_list, 200)

        # Test without parameters
        response = client.get("/ranking/table")
        assert response.status_code == 200
        assert json.loads(response.data) == mock_ranking_data_list

        # Test with season parameter
        response = client.get("/ranking/table?season=2022-2023")
        assert response.status_code == 200
        mock_get_ranking_list.assert_called_with(
            season="2022-2023", league="Premier League"
        )

        # Test with all parameters
        response = client.get("/ranking/table?season=2001-2002&league=La Liga")
        assert response.status_code == 200
        mock_get_ranking_list.assert_called_with(season="2001-2002", league="La Liga")

    @patch("premier_league.api.services.ranking_service.RankingService.get_ranking_csv")
    def test_get_standings_csv(self, mock_get_csv, create_temp_file, client, tmp_path):
        """Test GET /ranking/csv_file endpoint."""

        mock_get_csv.side_effect = lambda *args, **kwargs: (
            create_temp_file(
                "test_ranking.csv",
                "Pos,Team,Pts,W,D,L,GF,GA,GD\n1,Paris Saint-Germain,76,22,10,2,81,33,+48\n",
            ),
            200,
        )

        # Missing parameter
        response = client.get("/ranking/csv_file")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Test with required parameters
        response = client.get("/ranking/csv_file?filename=test_ranking")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_ranking.csv"
        )

        # Test with all parameters
        response = client.get(
            "/ranking/csv_file?filename=test_ranking&season=2022-2023&league=La Liga"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_ranking.csv"
        )
        mock_get_csv.assert_called_with(
            file_name="test_ranking", season="2022-2023", league="La Liga"
        )

    @patch(
        "premier_league.api.services.ranking_service.RankingService.get_ranking_json"
    )
    def test_get_standings_json(
        self, mock_get_json, mock_ranking_data, create_temp_file, client, tmp_path
    ):
        """Test GET /ranking/json_file endpoint."""
        mock_get_json.side_effect = lambda *args, **kwargs: (
            create_temp_file(
                "test_ranking.json",
                '{"ranking": [{"Pos": 1, "Team": "Paris Saint-Germain", "Pts": 76, "W": 22, "D": 10, "L": 2, "GF": 81, "GA": 33, "GD": "+48"}]}',
            ),
            200,
        )

        # Missing parameter
        response = client.get("/ranking/json_file?season=2022-2023")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Test with required parameters
        response = client.get("/ranking/json_file?filename=test_ranking")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_ranking.json"
        )

        # Test with all parameters
        response = client.get(
            "/ranking/json_file?filename=test_ranking&season=2022-2023&league=La Liga"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_ranking.json"
        )
        mock_get_json.assert_called_with(
            file_name="test_ranking", season="2022-2023", league="La Liga"
        )

    @patch("premier_league.api.services.ranking_service.RankingService.get_ranking_pdf")
    def test_get_standings_pdf(
        self, mock_get_pdf, mock_ranking_data, create_temp_file, client, tmp_path
    ):
        """Test GET /ranking/pdf_file endpoint."""
        mock_get_pdf.side_effect = lambda *args, **kwargs: (
            create_temp_file("test_ranking.pdf", str(mock_ranking_data)),
            200,
        )

        # Missing parameter
        response = client.get("/ranking/pdf_file?season=2022-2023")
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing filename parameter"}

        # Test with required parameters
        response = client.get("/ranking/pdf_file?filename=test_ranking")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_ranking.pdf"
        )

        # Test with all parameters
        response = client.get(
            "/ranking/pdf_file?filename=test_ranking&season=2022-2023&league=La Liga"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=test_ranking.pdf"
        )
        mock_get_pdf.assert_called_with(
            file_name="test_ranking", season="2022-2023", league="La Liga"
        )
