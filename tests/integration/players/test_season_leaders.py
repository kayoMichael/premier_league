import os
import re

import pytest

from premier_league.players.season_leaders import PlayerSeasonLeaders

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CASSETTE_DIR = os.path.join(TEST_DIR, "players", "cassettes")


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_premier_league_integration(vcr_config):
    """Test the PlayerSeasonLeaders class for Premier League."""
    # Define test cases
    test_cases = [
        {"league": "Premier League", "season": "2022-2023", "stat": "G"},
        {"league": "Premier League", "season": "2012-2013", "stat": "G"},
        {"league": "Premier League", "season": "2002-2003", "stat": "G"},
        {"league": "Premier League", "season": "1995-1996", "stat": "G"},
        {"league": "Premier League", "season": "2022-2023", "stat": "A"},
        {"league": "Premier League", "season": "2012-2013", "stat": "A"},
        {"league": "Premier League", "season": "2002-2003", "stat": "A"},
        {"league": "Premier League", "season": "1998-1999", "stat": "A"},
    ]

    results = []
    for case in test_cases:
        result = PlayerSeasonLeaders(
            league=case["league"],
            target_season=case["season"],
            stat_type=case["stat"],
            cache=False,
        ).get_top_stats_list()
        results.append((result, case["stat"], case["season"]))

    # Assert on all results
    for results, stat_type, season in results:
        assert isinstance(
            results, list
        ), f"Should return a list for {season} season {stat_type} stats of the Premier League"
        if stat_type == "A":
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Assists",
            ], f"Wrong Label For Result for {season} season Assist stats of the Premier League"
        else:
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Goals",
                "In Play Goals+Penalty",
            ], f"Wrong Label For Result for {season} season Assist stats of the Premier League"
        assert (
            len(results) > 10
        ), f"Should have more than 10 results for {season} season {stat_type} stats of the Premier League"
        for result in results[1:]:
            if stat_type == "A":
                assert (
                    len(result) == 4
                ), f"Assist results should have 4 columns for {season} season Assist stats of the Premier League"
                assert result[
                    3
                ].isdigit(), f"Assists should be a number for {season} season Assist stats of the Premier League"
            else:
                assert (
                    len(result) == 5
                ), f"Goals results should have 5 columns for {season} season Goal stats of the Premier League"
                assert result[
                    3
                ].isdigit(), f"Goals should be a number for {season} season Goal stats of the Premier League"
                assert re.match(
                    r"\(\d+\+\d+\)", result[4]
                ), f"In Play Goals+Penalty has the wrong format for {season} season Goal stats of the Premier League"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_la_liga_integration(vcr_config):
    """Test the PlayerSeasonLeaders class for La Liga."""
    # Define test cases
    test_cases = [
        {"league": "La Liga", "season": "2022-2023", "stat": "G"},
        {"league": "La Liga", "season": "2012-2013", "stat": "G"},
        {"league": "La Liga", "season": "2022-2023", "stat": "A"},
        {"league": "La Liga", "season": "2012-2013", "stat": "A"},
    ]

    results = []
    for case in test_cases:
        result = PlayerSeasonLeaders(
            league=case["league"],
            target_season=case["season"],
            stat_type=case["stat"],
            cache=False,
        ).get_top_stats_list()
        results.append((result, case["stat"], case["season"]))

    # Assert on all results
    for results, stat_type, season in results:
        assert isinstance(
            results, list
        ), f"Should return a list for {season} season {stat_type} stats of La Liga"
        if stat_type == "A":
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Assists",
            ], f"Wrong Label For Result for {season} season Assist stats of La Liga"
        else:
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Goals",
                "In Play Goals+Penalty",
            ], f"Wrong Label For Result for {season} season Assist stats of La Liga"
        assert (
            len(results) > 10
        ), f"Should have more than 10 results for {season} season {stat_type} stats of La Liga"
        for result in results[1:]:
            if stat_type == "A":
                assert (
                    len(result) == 4
                ), f"Assist results should have 4 columns for {season} season Assist stats of La Liga"
                assert result[
                    3
                ].isdigit(), f"Assists should be a number for {season} season Assist stats of La Liga"
            else:
                assert (
                    len(result) == 5
                ), f"Goals results should have 5 columns for {season} season Goal stats of La Liga"
                assert result[
                    3
                ].isdigit(), f"Goals should be a number for {season} season Goal stats of La Liga"
                assert re.match(
                    r"\(\d+\+\d+\)", result[4]
                ), f"In Play Goals+Penalty has the wrong format for {season} season Goal stats of La Liga"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_bundesliga_integration(vcr_config):
    """Test the PlayerSeasonLeaders class for Bundesliga."""
    # Define test cases
    test_cases = [
        {"league": "Bundesliga", "season": "2022-2023", "stat": "G"},
        {"league": "Bundesliga", "season": "2012-2013", "stat": "G"},
        {"league": "Bundesliga", "season": "2002-2003", "stat": "G"},
        {"league": "Bundesliga", "season": "1995-1996", "stat": "G"},
        {"league": "Bundesliga", "season": "1989-1990", "stat": "G"},
        {"league": "Bundesliga", "season": "2022-2023", "stat": "A"},
        {"league": "Bundesliga", "season": "2012-2013", "stat": "A"},
        {"league": "Bundesliga", "season": "2002-2003", "stat": "A"},
        {"league": "Bundesliga", "season": "1998-1999", "stat": "A"},
        {"league": "Bundesliga", "season": "1989-1990", "stat": "A"},
    ]

    results = []
    for case in test_cases:
        result = PlayerSeasonLeaders(
            league=case["league"],
            target_season=case["season"],
            stat_type=case["stat"],
            cache=False,
        ).get_top_stats_list()
        results.append((result, case["stat"], case["season"]))

    # Assert on all results
    for results, stat_type, season in results:
        assert isinstance(
            results, list
        ), f"Should return a list for {season} season {stat_type} stats of Bundesliga"
        if stat_type == "A":
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Assists",
            ], f"Wrong Label For Result for {season} season Assist stats of Bundesliga"
        else:
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Goals",
                "In Play Goals+Penalty",
            ], f"Wrong Label For Result for {season} season Assist stats of Bundesliga"
        assert (
            len(results) > 10
        ), f"Should have more than 10 results for {season} season {stat_type} stats of Bundesliga"
        for result in results[1:]:
            if stat_type == "A":
                assert (
                    len(result) == 4
                ), f"Assist results should have 4 columns for {season} season Assist stats of Bundesliga"
                assert result[
                    3
                ].isdigit(), f"Assists should be a number for {season} season Assist stats of Bundesliga"
            else:
                assert (
                    len(result) == 5
                ), f"Goals results should have 5 columns for {season} season Goal stats of Bundesliga"
                assert result[
                    3
                ].isdigit(), f"Goals should be a number for {season} season Goal stats of Bundesliga"
                assert re.match(
                    r"\(\d+\+\d+\)", result[4]
                ), f"In Play Goals+Pen Penalty has the wrong format for {season} season Goal stats of Bundesliga"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_serie_a_integration(vcr_config):
    """Test the PlayerSeasonLeaders class for Serie A."""
    # Define test cases
    test_cases = [
        {"league": "Serie A", "season": "2022-2023", "stat": "G"},
        {"league": "Serie A", "season": "2012-2013", "stat": "G"},
        {"league": "Serie A", "season": "2022-2023", "stat": "A"},
        {"league": "Serie A", "season": "2012-2013", "stat": "A"},
    ]

    results = []
    for case in test_cases:
        result = PlayerSeasonLeaders(
            league=case["league"],
            target_season=case["season"],
            stat_type=case["stat"],
            cache=False,
        ).get_top_stats_list()
        results.append((result, case["stat"], case["season"]))

    # Assert on all results
    for results, stat_type, season in results:
        assert isinstance(
            results, list
        ), f"Should return a list for {season} season {stat_type} stats of Serie A"
        if stat_type == "A":
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Assists",
            ], f"Wrong Label For Result for {season} season Assist stats of Serie A"
        else:
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Goals",
                "In Play Goals+Penalty",
            ], f"Wrong Label For Result for {season} season Assist stats of Serie A"
        assert (
            len(results) > 10
        ), f"Should have more than 10 results for {season} season {stat_type} stats of Serie A"
        for result in results[1:]:
            if stat_type == "A":
                assert (
                    len(result) == 4
                ), f"Assist results should have 4 columns for {season} season Assist stats of Serie A"
                assert result[
                    3
                ].isdigit(), f"Assists should be a number for {season} season Assist stats of Serie A"
            else:
                assert (
                    len(result) == 5
                ), f"Goals results should have 5 columns for {season} season Goal stats of Serie A"
                assert result[
                    3
                ].isdigit(), f"Goals should be a number for {season} season Goal stats of Serie A"
                assert re.match(
                    r"\(\d+\+\d+\)", result[4]
                ), f"In Play Goals+Penalty has the wrong format for {season} season Goal stats of Serie A"


@pytest.mark.vcr(vcr_cassette_dir=CASSETTE_DIR)
def test_ligue_1_integration(vcr_config):
    """Test the PlayerSeasonLeaders class for Ligue 1."""
    # Define test cases
    test_cases = [
        {"league": "Ligue 1", "season": "2022-2023", "stat": "G"},
        {"league": "Ligue 1", "season": "2012-2013", "stat": "G"},
        {"league": "Ligue 1", "season": "2022-2023", "stat": "A"},
        {"league": "Ligue 1", "season": "2012-2013", "stat": "A"},
    ]
    results = []
    for case in test_cases:
        result = PlayerSeasonLeaders(
            league=case["league"],
            target_season=case["season"],
            stat_type=case["stat"],
            cache=False,
        ).get_top_stats_list()
        results.append((result, case["stat"], case["season"]))

    # Assert on all results
    for results, stat_type, season in results:
        assert isinstance(
            results, list
        ), f"Should return a list for {season} season {stat_type} stats of Ligue 1"
        if stat_type == "A":
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Assists",
            ], f"Wrong Label For Result for {season} season Assist stats of Ligue 1"
        else:
            assert results[0] == [
                "Name",
                "Country",
                "Club",
                "Goals",
                "In Play Goals+Penalty",
            ], f"Wrong Label For Result for {season} season Assist stats of Ligue 1"
        assert (
            len(results) > 10
        ), f"Should have more than 10 results for {season} season {stat_type} stats of Ligue 1"
        for result in results[1:]:
            if stat_type == "A":
                assert (
                    len(result) == 4
                ), f"Assist results should have 4 columns for {season} season Assist stats of Ligue 1"
                assert result[
                    3
                ].isdigit(), f"Assists should be a number for {season} season Assist stats of Ligue 1"
            else:
                assert (
                    len(result) == 5
                ), f"Goals results should have 5 columns for {season} season Goal stats of Ligue 1"
                assert result[
                    3
                ].isdigit(), f"Goals should be a number for {season} season Goal stats of Ligue 1"
                assert re.match(
                    r"\(\d+\+\d+\)", result[4]
                ), f"In Play Goals+Penalty has the wrong format for {season} season Goal stats of Ligue 1"
