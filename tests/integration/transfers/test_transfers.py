import os
import re

import pytest

from premier_league import Transfers

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CASSETTE_DIR = os.path.join(TEST_DIR, "transfers", "cassettes")


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_premier_league_integration():
    """Test the Transfers Class for Premier League"""
    # Define test cases
    test_cases = [
        {"league": "Premier League", "season": "2022-2023"},
        {"league": "Premier League", "season": "2012-2013"},
        {"league": "Premier League", "season": "2002-2003"},
        {"league": "Premier League", "season": "1995-1996"},
        {"league": "Premier League", "season": "1984-1985"},
        {"league": "Premier League", "season": "1970-1971"},
        {"league": "Premier League", "season": "1963-1964"},
        {"league": "Premier League", "season": "1950-1951"},
        {"league": "Premier League", "season": "1947-1948"},
    ]

    results = []
    for case in test_cases:
        result = Transfers(
            league=case["league"], target_season=case["season"], cache=False
        )
        teams = result.get_all_current_teams()
        results.append(
            (
                result.transfer_in_table(teams[3]),
                result.transfer_out_table(teams[3]),
                case["season"],
            )
        )
    # Assert the results
    for transfer_in, transfer_out, season in results:
        assert transfer_in[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer in table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_in[0]}"
        assert transfer_out[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer out table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_out[0]}"

        for transfer in transfer_in[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"

        for transfer in transfer_out[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_la_liga_integration():
    """Test the Transfers Class for La Liga"""
    # Define test cases
    test_cases = [
        {"league": "La Liga", "season": "2022-2023"},
        {"league": "La Liga", "season": "2012-2013"},
        {"league": "La Liga", "season": "2002-2003"},
        {"league": "La Liga", "season": "1995-1996"},
        {"league": "La Liga", "season": "1984-1985"},
        {"league": "La Liga", "season": "1970-1971"},
        {"league": "La Liga", "season": "1963-1964"},
        {"league": "La Liga", "season": "1950-1951"},
        {"league": "La Liga", "season": "1947-1948"},
        {"league": "La Liga", "season": "1929-1930"},
    ]

    results = []
    for case in test_cases:
        result = Transfers(
            league=case["league"], target_season=case["season"], cache=False
        )
        teams = result.get_all_current_teams()
        results.append(
            (
                result.transfer_in_table(teams[3]),
                result.transfer_out_table(teams[3]),
                case["season"],
            )
        )
    # Assert the results
    for transfer_in, transfer_out, season in results:
        assert transfer_in[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer in table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_in[0]}"
        assert transfer_out[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer out table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_out[0]}"

        for transfer in transfer_in[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"

        for transfer in transfer_out[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_serie_a_integration():
    """Test the Transfers Class for Serie A"""
    # Define test cases
    test_cases = [
        {"league": "Serie A", "season": "2022-2023"},
        {"league": "Serie A", "season": "2012-2013"},
        {"league": "Serie A", "season": "2002-2003"},
        {"league": "Serie A", "season": "1995-1996"},
        {"league": "Serie A", "season": "1984-1985"},
        {"league": "Serie A", "season": "1970-1971"},
        {"league": "Serie A", "season": "1963-1964"},
        {"league": "Serie A", "season": "1950-1951"},
        {"league": "Serie A", "season": "1947-1948"},
    ]

    results = []
    for case in test_cases:
        result = Transfers(
            league=case["league"], target_season=case["season"], cache=False
        )
        teams = result.get_all_current_teams()
        results.append(
            (
                result.transfer_in_table(teams[3]),
                result.transfer_out_table(teams[3]),
                case["season"],
            )
        )
    # Assert the results
    for transfer_in, transfer_out, season in results:
        assert transfer_in[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer in table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_in[0]}"
        assert transfer_out[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer out table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_out[0]}"

        for transfer in transfer_in[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"

        for transfer in transfer_out[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_ligue_1_integration():
    """Test the Transfers Class for Ligue 1"""
    # Define test cases
    test_cases = [
        {"league": "Ligue 1", "season": "2022-2023"},
        {"league": "Ligue 1", "season": "2012-2013"},
        {"league": "Ligue 1", "season": "2002-2003"},
        {"league": "Ligue 1", "season": "1995-1996"},
        {"league": "Ligue 1", "season": "1984-1985"},
        {"league": "Ligue 1", "season": "1970-1971"},
        {"league": "Ligue 1", "season": "1963-1964"},
        {"league": "Ligue 1", "season": "1950-1951"},
        {"league": "Ligue 1", "season": "1947-1948"},
    ]

    results = []
    for case in test_cases:
        result = Transfers(
            league=case["league"], target_season=case["season"], cache=False
        )
        teams = result.get_all_current_teams()
        results.append(
            (
                result.transfer_in_table(teams[3]),
                result.transfer_out_table(teams[3]),
                case["season"],
            )
        )
    # Assert the results
    for transfer_in, transfer_out, season in results:
        assert transfer_in[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer in table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_in[0]}"
        assert transfer_out[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer out table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_out[0]}"

        for transfer in transfer_in[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"

        for transfer in transfer_out[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_bundesliga_integration(vcr_config):
    """Test the Transfers Class for Bundesliga"""
    # Define test cases
    test_cases = [
        {"league": "Bundesliga", "season": "2022-2023"},
        {"league": "Bundesliga", "season": "2012-2013"},
        {"league": "Bundesliga", "season": "2002-2003"},
        {"league": "Bundesliga", "season": "1995-1996"},
        {"league": "Bundesliga", "season": "1984-1985"},
        {"league": "Bundesliga", "season": "1970-1971"},
        {"league": "Bundesliga", "season": "1963-1964"},
    ]

    results = []
    for case in test_cases:
        result = Transfers(
            league=case["league"], target_season=case["season"], cache=False
        )
        teams = result.get_all_current_teams()
        results.append(
            (
                result.transfer_in_table(teams[3]),
                result.transfer_out_table(teams[3]),
                case["season"],
            )
        )
    # Assert the results
    for transfer_in, transfer_out, season in results:
        assert transfer_in[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer in table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_in[0]}"
        assert transfer_out[0] == [
            "Date",
            "Name",
            "Position",
            "Club",
        ], f"Header is not correct for {season} season transfer out table. Expected ['Date', 'Name', 'Position', 'Club'] but got {transfer_out[0]}"

        for transfer in transfer_in[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"

        for transfer in transfer_out[1:]:
            assert re.match(r"\d{2}/\d{2}", transfer[0])
            assert transfer[1]
            assert transfer[2] in ["FW", "MF", "DF", "AM", "DM", "GK"]
            assert transfer[3], "Length of Each row should be 4"
