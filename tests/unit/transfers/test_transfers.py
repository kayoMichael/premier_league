from unittest.mock import patch

import pytest

from premier_league.transfers.transfers import TeamNotFoundError, Transfers


class DummyTransfer:
    def __init__(self, header, data):
        self._header = header
        self._data = data

    def xpath(self, query):
        from premier_league.utils.xpath import PLAYERS

        if query == PLAYERS.TRANSFER_HEADER:
            return [self._header]
        elif query == PLAYERS.TRANSFER_DATA:
            return self._data
        return []


class TestTransfers:
    """Tests for the Transfers class."""

    @staticmethod
    def base_init_side_effect(self, url, target_season):
        """
        Side effect for BaseScrapper.__init__.
        Sets the url, target_season and a season attribute.
        """
        self.url = url
        self.target_season = target_season
        self.season = target_season if target_season else "2024-2025"

    @patch("premier_league.transfers.transfers.BaseScrapper.__init__", autospec=True)
    @patch("premier_league.transfers.transfers.Transfers.request_url_page")
    @patch("premier_league.transfers.transfers.Transfers._init_transfers_table")
    def test_init(self, mock_init_transfers_table, mock_request_page, mock_base_init):
        """Test initialization of the Transfers class."""
        mock_base_init.return_value = None
        mock_base_init.side_effect = TestTransfers.base_init_side_effect

        mock_request_page.return_value = "Mock Page"
        dummy_transfers = {
            "Team A": [
                [["Date", "Name", "Position", "Club"]],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/01", "Player A", "MID", "Club X"],
                ],
            ],
            "Team B": [
                [["Date", "Name", "Position", "Club"]],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["02/02", "Player B", "DEF", "Club Y"],
                ],
            ],
        }
        mock_init_transfers_table.return_value = dummy_transfers

        transfers = Transfers(target_season="2022-2023", league="Premier League")

        # Verify that league is lower-cased and attributes are set.
        assert transfers.league == "premier league"
        assert transfers.page == "Mock Page"
        assert transfers._season_top_players == dummy_transfers
        assert transfers.target_season == "2022-2023"

    def test_find_team(self):
        """Test the find_team method returns the closest match (or None)."""
        transfers = Transfers(target_season="2022-2023", league="Premier League")
        transfers._season_top_players = {
            "Team A": [[], []],
            "Team B": [[], []],
        }

        # Exact match.
        assert transfers.find_team("Team A") == "Team A"
        # Partial (case-insensitive) match.
        assert transfers.find_team("team b") == "Team B"
        # No match.
        assert transfers.find_team("Team C") is None

    def test_get_all_current_teams(self):
        """Test that get_all_current_teams returns a list of team names."""
        transfers = Transfers(target_season="2022-2023", league="Premier League")
        transfers._season_top_players = {"Team A": [[], []], "Team B": [[], []]}
        teams = transfers.get_all_current_teams()
        assert set(teams) == {"Team A", "Team B"}

    def test_transfer_in_table_and_out_table(self):
        """Test transfer_in_table and transfer_out_table return correct data or raise errors."""
        transfers = Transfers(target_season="2022-2023", league="Premier League")
        dummy_data = {
            "Team A": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/01", "Player A", "MID", "Club X"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["02/02", "Player B", "DEF", "Club Y"],
                ],
            ]
        }
        transfers._season_top_players = dummy_data

        # Valid team.
        assert transfers.transfer_in_table("Team A") == [
            ["Date", "Name", "Position", "Club"],
            ["01/01", "Player A", "MID", "Club X"],
        ]
        assert transfers.transfer_out_table("Team A") == [
            ["Date", "Name", "Position", "Club"],
            ["02/02", "Player B", "DEF", "Club Y"],
        ]

        # If team is not found, a TeamNotFoundError should be raised.
        with pytest.raises(TeamNotFoundError):
            transfers.transfer_in_table("Nonexistent Team")
        with pytest.raises(TeamNotFoundError):
            transfers.transfer_out_table("Nonexistent Team")

    @patch("premier_league.transfers.transfers.export_to_csv")
    def test_transfer_csv(self, mock_export_csv):
        """Test the transfer_csv method calls export_to_csv with proper arguments."""
        transfers = Transfers(target_season="2022-2023", league="Premier League")
        dummy_data = {
            "Team A": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/01", "Player A", "MID", "Club X"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["02/02", "Player B", "DEF", "Club Y"],
                ],
            ]
        }
        transfers._season_top_players = dummy_data

        # Test export for both transfer types.
        transfers.transfer_csv("Team A", "test_file", transfer_type="both")
        mock_export_csv.assert_called_with(
            "test_file",
            dummy_data["Team A"][0],
            dummy_data["Team A"][1],
            f"Team A {transfers.season} Transfers In",
            f"Team A {transfers.season} Transfers Out",
        )
        mock_export_csv.reset_mock()

        # Test export for "in" transfers only.
        transfers.transfer_csv("Team A", "test_file", transfer_type="in")
        mock_export_csv.assert_called_with(
            "test_file",
            dummy_data["Team A"][0],
            header=f"Team A {transfers.season} Transfers In",
        )
        mock_export_csv.reset_mock()

        # Test export for "out" transfers only.
        transfers.transfer_csv("Team A", "test_file", transfer_type="out")
        mock_export_csv.assert_called_with(
            "test_file",
            dummy_data["Team A"][1],
            header=f"Team A {transfers.season} Transfers Out",
        )

    @patch("premier_league.transfers.transfers.export_to_json")
    def test_transfer_json(self, mock_export_json):
        """Test the transfer_json method calls export_to_json with proper arguments."""
        transfers = Transfers(target_season="2022-2023", league="Premier League")
        dummy_data = {
            "Team A": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/01", "Player A", "MID", "Club X"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["02/02", "Player B", "DEF", "Club Y"],
                ],
            ]
        }
        transfers._season_top_players = dummy_data

        # Test export for both transfer types.
        transfers.transfer_json("Team A", "test_file", transfer_type="both")
        mock_export_json.assert_called_with(
            "test_file",
            dummy_data["Team A"][0],
            dummy_data["Team A"][1],
            f"Team A {transfers.season} Transfers In",
            f"Team A {transfers.season} Transfers Out",
        )
        mock_export_json.reset_mock()

        # Test export for "in" transfers only.
        transfers.transfer_json("Team A", "test_file", transfer_type="in")
        mock_export_json.assert_called_with("test_file", dummy_data["Team A"][0])
        mock_export_json.reset_mock()

        # Test export for "out" transfers only.
        transfers.transfer_json("Team A", "test_file", transfer_type="out")
        mock_export_json.assert_called_with("test_file", dummy_data["Team A"][1])

    def test_print_transfer_table(self, capsys):
        """Test that print_transfer_table prints transfer tables correctly."""
        transfers = Transfers(target_season="2022-2023", league="Premier League")
        dummy_data = {
            "Team A": [
                [
                    ["Date", "Name", "Position", "Club"],
                    ["01/01", "Player A", "MID", "Club X"],
                ],
                [
                    ["Date", "Name", "Position", "Club"],
                    ["02/02", "Player B", "DEF", "Club Y"],
                ],
            ]
        }
        transfers._season_top_players = dummy_data

        # Patch find_team to always return "Team A".
        with patch.object(transfers, "find_team", return_value="Team A"):
            transfers.print_transfer_table("Team A")
            captured = capsys.readouterr().out
            # Check that the output contains the season and the transfer rows.
            assert f"Transfers {transfers.season}" in captured
            assert "01/01" in captured
            assert "02/02" in captured

    def test_init_transfers_table(self):
        """Test the _init_transfers_table method for proper processing of transfer data."""
        transfers = Transfers(target_season="2022-2023", league="Premier League")
        # Use the PLAYERS constants from the xpath module.
        from premier_league.utils.xpath import PLAYERS

        # Create a dummy transfer element.
        dummy_transfer = DummyTransfer(
            "Team A » Some Info",
            [
                "Header",
                "01/01",
                "Player A",
                "MID",
                "Club X",
                "Out",
                "02/02",
                "Player B",
                "DEF",
                "Club Y",
            ],
        )
        # Patch get_list_by_xpath to return our dummy element.
        with patch.object(
            transfers, "get_list_by_xpath", return_value=[dummy_transfer]
        ) as mock_get_list:
            # Patch clean_xml_text to act as an identity function.
            with patch(
                "premier_league.transfers.transfers.clean_xml_text",
                side_effect=lambda x: x,
            ):
                result = transfers._init_transfers_table()
                assert "Team A" in result
                # Check that the header rows are present.
                assert result["Team A"][0][0] == ["Date", "Name", "Position", "Club"]
                assert result["Team A"][1][0] == ["Date", "Name", "Position", "Club"]
                # For transfer In, only the header should be present.
                assert len(result["Team A"][0]) == 1
                # For transfer Out, header plus two rows (one from before the date switch and one from after).
                assert len(result["Team A"][1]) == 3
            mock_get_list.assert_called_once_with(PLAYERS.TRANSFER_TABLES, False)
