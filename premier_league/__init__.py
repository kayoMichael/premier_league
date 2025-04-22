from premier_league.match_statistics.match_statistics import MatchStatistics
from premier_league.players.season_leaders import PlayerSeasonLeaders
from premier_league.ranking.ranking_table import RankingTable
from premier_league.transfers.transfers import TeamNotFoundError, Transfers


# Lazy Import Run Server
def run_server(*args, **kwargs):
    try:
        from premier_league.api.app import run_server as real_run
    except ImportError:
        raise ImportError(
            "This function requires Flask. Install it with:\n"
            "    pip install premier_league[flask] \n"
            "Install all options with:\n"
            "    pip install premier_league[all]"
        )
    return real_run(*args, **kwargs)


__all__ = [
    "RankingTable",
    "PlayerSeasonLeaders",
    "Transfers",
    "MatchStatistics",
    "run_server",
]
