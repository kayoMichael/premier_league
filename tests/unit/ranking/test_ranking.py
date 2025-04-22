import os
from unittest.mock import MagicMock, PropertyMock, patch

from reportlab.lib.pagesizes import A3

from premier_league import RankingTable


class TestRankingTable:
    """Tests for the RankingTable class."""

    @staticmethod
    def base_init_side_effect(self, url, target_season, season_limit, cache):
        """
        Mocks the attribute setting and any post-init processing of BaseScrapper.
        """
        self.url = url
        self.target_season = target_season
        self.season_limit = season_limit
        self.cache = cache
        self.__post_init__()

    @patch("premier_league.ranking.ranking_table.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.ranking.ranking_table.RankingTable.request_url_page")
    @patch("premier_league.ranking.ranking_table.RankingTable._init_ranking_table")
    def test_init(self, mock_init_table, mock_request_page, mock_base_init):
        """Test the initialization of the RankingTable class."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect

        # Set up mocks for the methods called in __init__
        mock_request_page.return_value = "<html>Mock Page</html>"
        sample_ranking = [
            ["Pos", "Team", "Pld", "W", "D", "L", "GF", "GA", "GD", "Pts"],
            ["1", "Liverpool", "29", "21", "7", "1", "69", "27", "+42", "70"],
            ["2", "Arsenal", "29", "16", "10", "3", "53", "24", "+29", "3"],
        ]
        mock_init_table.return_value = sample_ranking

        ranking = RankingTable(league="premier league", target_season="2022-2023")

        assert ranking.league == "Premier League"
        assert ranking.page == "<html>Mock Page</html>"
        assert ranking.ranking_list == sample_ranking
        assert ranking.target_season == "2022-2023"

        mock_base_init.assert_called_once()
        mock_request_page.assert_called_once()
        mock_init_table.assert_called_once()

    @patch("premier_league.ranking.ranking_table.export_to_csv")
    @patch("premier_league.ranking.ranking_table.BaseScrapper.__init__")
    @patch("premier_league.ranking.ranking_table.RankingTable.request_url_page")
    @patch("premier_league.ranking.ranking_table.RankingTable._init_ranking_table")
    def test_get_ranking_csv(
        self, mock_init_table, mock_request_page, mock_base_init, mock_export_csv
    ):
        """Test the get_ranking_csv method."""
        mock_base_init.return_value = None
        mock_request_page.return_value = "<html>Mock Page</html>"
        sample_ranking = [["Rank", "Team", "Points"], ["1", "TeamA", "80"]]
        mock_init_table.return_value = sample_ranking

        ranking = RankingTable(league="Premier League", target_season="2022-2023")
        ranking.get_ranking_csv(file_name="test_file", header="Test Header")
        mock_export_csv.assert_called_once_with(
            "test_file", sample_ranking, "Test Header"
        )

    @patch("premier_league.ranking.ranking_table.export_to_json")
    @patch("premier_league.ranking.ranking_table.BaseScrapper.__init__")
    @patch("premier_league.ranking.ranking_table.RankingTable.request_url_page")
    @patch("premier_league.ranking.ranking_table.RankingTable._init_ranking_table")
    def test_get_ranking_json(
        self, mock_init_table, mock_request_page, mock_base_init, mock_export_json
    ):
        """Test the get_ranking_json method."""
        mock_base_init.return_value = None
        mock_request_page.return_value = "<html>Mock Page</html>"
        sample_ranking = [["Rank", "Team", "Points"], ["1", "TeamA", "80"]]
        mock_init_table.return_value = sample_ranking

        ranking = RankingTable(league="Premier League", target_season="2022-2023")
        ranking.get_ranking_json(file_name="test_file", header="Test Header")
        mock_export_json.assert_called_once_with(
            "test_file", sample_ranking, header_1="Test Header"
        )

    @patch("premier_league.ranking.ranking_table.export_to_dict")
    @patch("premier_league.ranking.ranking_table.BaseScrapper.__init__")
    @patch("premier_league.ranking.ranking_table.RankingTable.request_url_page")
    @patch("premier_league.ranking.ranking_table.RankingTable._init_ranking_table")
    def test_get_ranking_dict(
        self, mock_init_table, mock_request_page, mock_base_init, mock_export_dict
    ):
        """Test the get_ranking_dict method."""
        mock_base_init.return_value = None
        mock_request_page.return_value = "<html>Mock Page</html>"
        sample_ranking = [["Rank", "Team", "Points"], ["1", "TeamA", "80"]]
        mock_init_table.return_value = sample_ranking

        ranking = RankingTable(league="Premier League", target_season="2022-2023")
        ranking.get_ranking_dict(header="Test Header")
        mock_export_dict.assert_called_once_with(sample_ranking, header_1="Test Header")

    @patch("reportlab.pdfgen.canvas.Canvas")
    @patch("reportlab.platypus.Table")
    @patch("premier_league.ranking.ranking_table.BaseScrapper.__init__")
    @patch("premier_league.ranking.ranking_table.RankingTable.request_url_page")
    @patch("premier_league.ranking.ranking_table.RankingTable._init_ranking_table")
    def test_get_ranking_pdf(
        self,
        mock_init_table,
        mock_request_page,
        mock_base_init,
        mock_Table,
        mock_canvas,
    ):
        """Test the get_ranking_pdf method."""
        mock_base_init.return_value = None
        mock_request_page.return_value = "<html>Mock Page</html>"
        sample_ranking = [["Rank", "Team", "Points"], ["1", "TeamA", "80"]]
        mock_init_table.return_value = sample_ranking

        mock_pdf = MagicMock()
        mock_canvas.return_value = mock_pdf

        mock_table_instance = MagicMock()
        mock_table_instance.wrapOn.return_value = (500, 400)
        mock_Table.return_value = mock_table_instance

        with patch.object(
            RankingTable, "season", new_callable=PropertyMock
        ) as mock_season:
            mock_season.return_value = "2022-2023"

            with patch.object(
                RankingTable, "_find_european_qualification_spot", return_value=[]
            ) as mock_euro_spots:
                ranking = RankingTable(
                    league="Premier League", target_season="2022-2023"
                )
                ranking.get_ranking_pdf(file_name="test_file", dir="test")

                mock_canvas.assert_called_once_with("test/test_file.pdf", pagesize=A3)
                mock_Table.assert_called_once_with(sample_ranking)
                mock_table_instance.setStyle.assert_called_once()
                mock_pdf.save.assert_called_once()
                mock_euro_spots.assert_called_once()
                if os.path.exists("test") and not os.listdir("test"):
                    os.rmdir("test")
