import os
import re

import pytest

from premier_league import RankingTable
from premier_league.utils.methods import is_float_string

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CASSETTE_DIR = os.path.join(TEST_DIR, "ranking", "cassettes")
POTENTIAL_HEADER = [
    "Pos",
    "Team",
    "Pld",
    "W",
    "D",
    "L",
    "GF",
    "GA",
    "GD",
    "Pts",
    "GAv",
    "GR",
    "GRA",
]


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_premier_league_integration(vcr_config):
    """Test the RankingTable class for Premier League."""
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
        result = RankingTable(
            league=case["league"], target_season=case["season"], cache=False
        ).get_ranking_list()
        results.append((result, case["season"]))

    # Assert on all results
    for result, season in results:
        header = result[0]
        data = result[1:]
        for title in header:
            assert (
                title in POTENTIAL_HEADER
            ), f"Header {title} not in {POTENTIAL_HEADER} for {season} season of the Premier League"
        for row in data:
            assert (
                len(row) == 10
            ), f"Results should have 10 columns for {season} season of the Premier League"
            assert row[
                0
            ].isdigit(), (
                f"Position should be a number for {season} season of the Premier League"
            )
            assert row[
                2
            ].isdigit(), (
                f"Played should be a number for {season} season of the Premier League"
            )
            assert row[
                3
            ].isdigit(), (
                f"Won should be a number for {season} season of the Premier League"
            )
            assert row[
                4
            ].isdigit(), (
                f"Drawn should be a number for {season} season of the Premier League"
            )
            assert row[
                5
            ].isdigit(), (
                f"Lost should be a number for {season} season of the Premier League"
            )
            assert row[
                6
            ].isdigit(), f"Goals For should be a number for {season} season of the Premier League"
            assert row[
                7
            ].isdigit(), f"Goals Against should be a number for {season} season of the Premier League"
            if header[8] != "GD":
                assert is_float_string(
                    row[8]
                ), f"Goal Ratio should be a float for {season} season of the Premier League"
            else:
                assert re.match(
                    r"[+\−\-]?\d+", row[8]
                ), f"Goal Difference should be a number for {season} season of the Premier League"
            assert row[
                9
            ].isdigit(), (
                f"Points should be a number for {season} season of the Premier League"
            )


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_la_liga_integration(vcr_config):
    """Test the RankingTable class for La Liga."""
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
        {"league": "La Liga", "season": "1933-1934"},
    ]

    results = []
    for case in test_cases:
        result = RankingTable(
            league=case["league"], target_season=case["season"], cache=False
        ).get_ranking_list()
        results.append((result, case["season"]))

    # Assert on all results
    for result, season in results:
        header = result[0]
        data = result[1:]
        for title in header:
            assert (
                title in POTENTIAL_HEADER
            ), f"Header {title} not in {POTENTIAL_HEADER} for {season} season of La Liga"
        for row in data:
            assert (
                len(row) == 10
            ), f"Results should have 10 columns for {season} season of La Liga"
            assert row[
                0
            ].isdigit(), f"Position should be a number for {season} season of La Liga"
            assert row[
                2
            ].isdigit(), f"Played should be a number for {season} season of La Liga"
            assert row[
                3
            ].isdigit(), f"Won should be a number for {season} season of La Liga"
            assert row[
                4
            ].isdigit(), f"Drawn should be a number for {season} season of La Liga"
            assert row[
                5
            ].isdigit(), f"Lost should be a number for {season} season of La Liga"
            assert row[
                6
            ].isdigit(), f"Goals For should be a number for {season} season of La Liga"
            assert row[
                7
            ].isdigit(), (
                f"Goals Against should be a number for {season} season of La Liga"
            )
            if header[8] != "GD":
                assert is_float_string(
                    row[8]
                ), f"Goal Ratio should be a float for {season} season of La Liga"
            else:
                assert re.match(
                    r"[+\−\-]?\d+", row[8]
                ), f"Goal Difference should be a number for {season} season of La Liga"
            assert row[
                9
            ].isdigit(), f"Points should be a number for {season} season of La Liga"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_bundesliga_integration(vcr_config):
    """Test the RankingTable class for Bundesliga."""
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
        result = RankingTable(
            league=case["league"], target_season=case["season"], cache=False
        ).get_ranking_list()
        results.append((result, case["season"]))

    # Assert on all results
    for result, season in results:
        header = result[0]
        data = result[1:]
        for title in header:
            assert (
                title in POTENTIAL_HEADER
            ), f"Header {title} not in {POTENTIAL_HEADER} for {season} season of Bundesliga"
        for row in data:
            assert (
                len(row) == 10
            ), f"Results should have 10 columns for {season} season of Bundesliga"
            assert row[
                0
            ].isdigit(), (
                f"Position should be a number for {season} season of Bundesliga"
            )
            assert row[
                2
            ].isdigit(), f"Played should be a number for {season} season of Bundesliga"
            assert row[
                3
            ].isdigit(), f"Won should be a number for {season} season of Bundesliga"
            assert row[
                4
            ].isdigit(), f"Drawn should be a number for {season} season of Bundesliga"
            assert row[
                5
            ].isdigit(), f"Lost should be a number for {season} season of Bundesliga"
            assert row[
                6
            ].isdigit(), (
                f"Goals For should be a number for {season} season of Bundesliga"
            )
            assert row[
                7
            ].isdigit(), (
                f"Goals Against should be a number for {season} season of Bundesliga"
            )
            if header[8] != "GD":
                assert is_float_string(
                    row[8]
                ), f"Goal Ratio should be a float for {season} season of Bundesliga"
            else:
                assert re.match(
                    r"[+\−\-]?\d+", row[8]
                ), f"Goal Difference should be a number for {season} season of Bundesliga"
            assert row[
                9
            ].isdigit(), f"Points should be a number for {season} season of Bundesliga"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_serie_a_integrations(vcr_config):
    """Test the RankingTable class for Bundesliga."""
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
        {"league": "Serie A", "season": "1946-1947"},
        {"league": "Serie A", "season": "1929-1930"},
    ]
    results = []
    for case in test_cases:
        result = RankingTable(
            league=case["league"], target_season=case["season"], cache=False
        ).get_ranking_list()
        results.append((result, case["season"]))

    # Assert on All Results
    for result, season in results:
        header = result[0]
        data = result[1:]
        for title in header:
            assert (
                title in POTENTIAL_HEADER
            ), f"Header {title} not in {POTENTIAL_HEADER} for {season} season of Serie A"
        for row in data:
            assert (
                len(row) == 10
            ), f"Results should have 10 columns for {season} season of Serie A"
            assert row[
                0
            ].isdigit(), f"Position should be a number for {season} season of Serie A"
            assert row[
                2
            ].isdigit(), f"Played should be a number for {season} season of Serie A"
            assert row[
                3
            ].isdigit(), f"Won should be a number for {season} season of Serie A"
            assert row[
                4
            ].isdigit(), f"Drawn should be a number for {season} season of Serie A"
            assert row[
                5
            ].isdigit(), f"Lost should be a number for {season} season of Serie A"
            assert row[
                6
            ].isdigit(), f"Goals For should be a number for {season} season of Serie A"
            assert row[
                7
            ].isdigit(), (
                f"Goals Against should be a number for {season} season of Serie A"
            )
            if header[8] != "GD":
                assert is_float_string(
                    row[8]
                ), f"Goal Ratio should be a float for {season} season of Serie A"
            else:
                assert re.match(
                    r"[+\−\-]?\d+", row[8]
                ), f"Goal Difference should be a number for {season} season of Serie A"
            assert row[
                9
            ].isdigit(), f"Points should be a number for {season} season of Serie A"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_ligue_1_integration(vcr_config):
    """Test the RankingTable class for Ligue 1."""
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
        result = RankingTable(
            league=case["league"], target_season=case["season"], cache=False
        ).get_ranking_list()
        results.append((result, case["season"]))

    # Assert on All Results
    for result, season in results:
        header = result[0]
        data = result[1:]
        for title in header:
            assert (
                title in POTENTIAL_HEADER
            ), f"Header {title} not in {POTENTIAL_HEADER} for {season} season of Ligue 1"
        for row in data:
            assert (
                len(row) == 10
            ), f"Results should have 10 columns for {season} season of Ligue 1"
            assert row[
                0
            ].isdigit(), f"Position should be a number for {season} season of Ligue 1"
            assert row[
                2
            ].isdigit(), f"Played should be a number for {season} season of Ligue 1"
            assert row[
                3
            ].isdigit(), f"Won should be a number for {season} season of Ligue 1"
            assert row[
                4
            ].isdigit(), f"Drawn should be a number for {season} season of Ligue 1"
            assert row[
                5
            ].isdigit(), f"Lost should be a number for {season} season of Ligue 1"
            assert row[
                6
            ].isdigit(), f"Goals For should be a number for {season} season of Ligue 1"
            assert row[
                7
            ].isdigit(), (
                f"Goals Against should be a number for {season} season of Ligue 1"
            )
            if header[8] != "GD":
                assert is_float_string(
                    row[8]
                ), f"Goal Ratio should be a float for {season} season of Ligue 1"
            else:
                assert re.match(
                    r"[+\−\-]?\d+", row[8]
                ), f"Goal Difference should be a number for {season} season of Ligue 1"
            assert row[
                9
            ].isdigit(), f"Points should be a number for {season} season of Ligue 1"
