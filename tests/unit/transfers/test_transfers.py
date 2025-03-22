from unittest.mock import MagicMock, PropertyMock, patch

from premier_league.transfers.transfers import TeamNotFoundError, Transfers


class TestTransfers:
    """Tests for the Transfers class."""

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

    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_init(
        self, mock_season_limit, mock_init_table, mock_request_page, mock_base_init
    ):
        """Test the initialization of the Transfers class."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946

        # Set up mocks for the methods called in __init__
        mock_request_page.return_value = "<html>Mock Page</html>"
        sample_transfers = {
            "Liverpool": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "John Doe", "Forward", "Arsenal"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "Jane Smith", "Midfielder", "Chelsea"],
                ],
            ],
            "Arsenal": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["02/07", "Bob Johnson", "Defender", "Manchester United"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["02/07", "Alice Brown", "Goalkeeper", "Tottenham"],
                ],
            ],
        }
        mock_init_table.return_value = sample_transfers

        transfers = Transfers(target_season="2022-2023", league="premier league")

        assert transfers.league == "premier league"
        assert transfers.page == "<html>Mock Page</html>"
        assert transfers._season_top_players == sample_transfers
        assert transfers.target_season == "2022-2023"

        mock_base_init.assert_called_once()
        mock_request_page.assert_called_once()
        mock_init_table.assert_called_once()
        mock_season_limit.assert_called_once()

    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_find_team(
        self, mock_season_limit, mock_init_table, mock_request_page, mock_base_init
    ):
        """Test the find_team method."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946
        mock_request_page.return_value = "<html>Mock Page</html>"

        sample_transfers = {
            "Liverpool": [[], []],
            "Manchester United": [[], []],
            "Arsenal FC": [[], []],
        }
        mock_init_table.return_value = sample_transfers

        transfers = Transfers(target_season="2022-2023")

        # Test exact match
        assert transfers.find_team("Liverpool") == "Liverpool"

        # Test partial match
        assert transfers.find_team("united") == "Manchester United"

        # Test case insensitive match
        assert transfers.find_team("arsenal") == "Arsenal FC"

        # Test non-existent team
        assert transfers.find_team("Nonexistent Team") is None

    @patch("builtins.print")
    @patch("premier_league.transfers.transfers.PrettyTable")
    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_print_transfer_table(
        self,
        mock_season_limit,
        mock_init_table,
        mock_request_page,
        mock_base_init,
        mock_pretty_table,
        mock_print,
    ):
        """Test the print_transfer_table method."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946
        mock_request_page.return_value = "<html>Mock Page</html>"

        sample_transfers = {
            "Liverpool": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "John Doe", "Forward", "Arsenal"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "Jane Smith", "Midfielder", "Chelsea"],
                ],
            ]
        }
        mock_init_table.return_value = sample_transfers

        # Mock PrettyTable
        mock_in_table = MagicMock()
        mock_out_table = MagicMock()
        mock_pretty_table.side_effect = [mock_in_table, mock_out_table]

        # Create a property mock for the season attribute
        with patch.object(
            Transfers, "season", new_callable=PropertyMock
        ) as mock_season:
            mock_season.return_value = "2022-2023"

            transfers = Transfers(target_season="2022-2023")
            transfers.print_transfer_table("Liverpool")

            # Assert add_row was called
            mock_in_table.add_row.assert_called_once()
            mock_out_table.add_row.assert_called_once()

            # Assert print was called
            assert mock_print.call_count >= 4  # At least 4 print calls

    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_transfer_in_table(
        self, mock_season_limit, mock_init_table, mock_request_page, mock_base_init
    ):
        """Test the transfer_in_table method."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946
        mock_request_page.return_value = "<html>Mock Page</html>"

        sample_transfers = {
            "Liverpool": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "John Doe", "Forward", "Arsenal"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "Jane Smith", "Midfielder", "Chelsea"],
                ],
            ]
        }
        mock_init_table.return_value = sample_transfers

        transfers = Transfers(target_season="2022-2023")

        # Test successful transfer_in_table retrieval
        result = transfers.transfer_in_table("Liverpool")
        assert result == sample_transfers["Liverpool"][0]

        # Test TeamNotFoundError
        with patch.object(Transfers, "find_team", return_value=None):
            with patch.object(
                Transfers, "season", new_callable=PropertyMock
            ) as mock_season:
                mock_season.return_value = "2022-2023"
                try:
                    transfers.transfer_in_table("Nonexistent Team")
                    assert False, "Expected TeamNotFoundError"
                except TeamNotFoundError as e:
                    assert "not found in the 2022-2023 Premier League season" in str(e)

    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_transfer_out_table(
        self, mock_season_limit, mock_init_table, mock_request_page, mock_base_init
    ):
        """Test the transfer_out_table method."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946
        mock_request_page.return_value = "<html>Mock Page</html>"

        sample_transfers = {
            "Liverpool": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "John Doe", "Forward", "Arsenal"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/07", "Jane Smith", "Midfielder", "Chelsea"],
                ],
            ]
        }
        mock_init_table.return_value = sample_transfers

        transfers = Transfers(target_season="2022-2023")

        # Test successful transfer_out_table retrieval
        result = transfers.transfer_out_table("Liverpool")
        assert result == sample_transfers["Liverpool"][1]

        # Test TeamNotFoundError
        with patch.object(Transfers, "find_team", return_value=None):
            with patch.object(
                Transfers, "season", new_callable=PropertyMock
            ) as mock_season:
                mock_season.return_value = "2022-2023"
                try:
                    transfers.transfer_out_table("Nonexistent Team")
                    assert False, "Expected TeamNotFoundError"
                except TeamNotFoundError as e:
                    assert "not found in the 2022-2023 Premier League season" in str(e)

    @patch("premier_league.transfers.transfers.export_to_csv")
    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_transfer_csv(
        self,
        mock_season_limit,
        mock_init_table,
        mock_request_page,
        mock_base_init,
        mock_export_csv,
    ):
        """Test the transfer_csv method."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946
        mock_request_page.return_value = "<html>Mock Page</html>"

        in_data = [
            ["Date", "Name", "Position", "Club"],
            ["01/07", "John Doe", "Forward", "Arsenal"],
        ]
        out_data = [
            ["Date", "Name", "Position", "Club"],
            ["01/07", "Jane Smith", "Midfielder", "Chelsea"],
        ]

        sample_transfers = {"Liverpool": [in_data, out_data]}
        mock_init_table.return_value = sample_transfers

        # Create property mock for season
        with patch.object(
            Transfers, "season", new_callable=PropertyMock
        ) as mock_season:
            mock_season.return_value = "2022-2023"

            # Test transfer_csv with 'both' type
            transfers = Transfers(target_season="2022-2023")
            transfers.transfer_csv("Liverpool", "test_file", "both")
            mock_export_csv.assert_called_once_with(
                "test_file",
                in_data,
                out_data,
                "Liverpool 2022-2023 Transfers In",
                "Liverpool 2022-2023 Transfers Out",
            )
            mock_export_csv.reset_mock()

            # Test transfer_csv with 'in' type
            transfers.transfer_csv("Liverpool", "test_file", "in")
            mock_export_csv.assert_called_once_with(
                "test_file", in_data, header="Liverpool 2022-2023 Transfers In"
            )
            mock_export_csv.reset_mock()

            # Test transfer_csv with 'out' type
            transfers.transfer_csv("Liverpool", "test_file", "out")
            mock_export_csv.assert_called_once_with(
                "test_file", out_data, header="Liverpool 2022-2023 Transfers Out"
            )

    @patch("premier_league.transfers.transfers.export_to_json")
    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_transfer_json(
        self,
        mock_season_limit,
        mock_init_table,
        mock_request_page,
        mock_base_init,
        mock_export_json,
    ):
        """Test the transfer_json method."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946
        mock_request_page.return_value = "<html>Mock Page</html>"

        in_data = [
            ["Date", "Name", "Position", "Club"],
            ["01/07", "John Doe", "Forward", "Arsenal"],
        ]
        out_data = [
            ["Date", "Name", "Position", "Club"],
            ["01/07", "Jane Smith", "Midfielder", "Chelsea"],
        ]

        sample_transfers = {"Liverpool": [in_data, out_data]}
        mock_init_table.return_value = sample_transfers

        # Create property mock for season
        with patch.object(
            Transfers, "season", new_callable=PropertyMock
        ) as mock_season:
            mock_season.return_value = "2022-2023"

            # Test transfer_json with 'both' type
            transfers = Transfers(target_season="2022-2023")
            transfers.transfer_json("Liverpool", "test_file", "both")
            mock_export_json.assert_called_once_with(
                "test_file",
                in_data,
                out_data,
                "Liverpool 2022-2023 Transfers In",
                "Liverpool 2022-2023 Transfers Out",
            )
            mock_export_json.reset_mock()

            # Test transfer_json with 'in' type
            transfers.transfer_json("Liverpool", "test_file", "in")
            mock_export_json.assert_called_once_with("test_file", in_data)
            mock_export_json.reset_mock()

            # Test transfer_json with 'out' type
            transfers.transfer_json("Liverpool", "test_file", "out")
            mock_export_json.assert_called_once_with("test_file", out_data)

    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    @patch("premier_league.transfers.transfers.Transfers.find_season_limit")
    def test_get_all_current_teams(
        self, mock_season_limit, mock_init_table, mock_request_page, mock_base_init
    ):
        """Test the get_all_current_teams method."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = self.base_init_side_effect
        mock_season_limit.return_value = 1946
        mock_request_page.return_value = "<html>Mock Page</html>"

        sample_transfers = {
            "Liverpool": [[], []],
            "Manchester United": [[], []],
            "Arsenal": [[], []],
        }
        mock_init_table.return_value = sample_transfers

        transfers = Transfers(target_season="2022-2023")
        teams = transfers.get_all_current_teams()

        assert teams == ["Liverpool", "Manchester United", "Arsenal"]
        assert len(teams) == 3

    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    def test_find_season_limit(
        self, mock_init_table, mock_request_page, mock_base_init
    ):
        """Test the find_season_limit method."""
        mock_base_init.return_value = None
        mock_init_table.return_value = None
        mock_request_page.return_value = "<html>Mock Page</html>"

        # Test Premier League
        transfers = Transfers(league="premier league")
        assert transfers.find_season_limit() == 1946

        # Test La Liga
        transfers = Transfers(league="la liga")
        assert transfers.find_season_limit() == 1928

        # Test Serie A
        transfers = Transfers(league="serie a")
        assert transfers.find_season_limit() == 1946

        # Test Ligue 1
        transfers = Transfers(league="ligue 1")
        assert transfers.find_season_limit() == 1945

        # Test Bundesliga
        transfers = Transfers(league="bundesliga")
        assert transfers.find_season_limit() == 1963
