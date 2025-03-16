import pdb


class PredictorURL:
    BASE_URLS = {
        "Premier League": "https://fbref.com/en/comps/9/{SEASON}/schedule/{SEASON}-Premier-League-Scores-and-Fixtures",
        "La Liga": "https://fbref.com/en/comps/12/{SEASON}/schedule/{SEASON}-La-Liga-Scores-and-Fixtures",
        "Serie A": "https://fbref.com/en/comps/11/{SEASON}/schedule/{SEASON}-Serie-A-Scores-and-Fixtures",
        "Ligue 1": "https://fbref.com/en/comps/13/{SEASON}/schedule/{SEASON}-League-1-Scores-and-Fixtures",
        "Fußball-Bundesliga": "https://fbref.com/en/comps/20/{SEASON}/schedule/{SEASON}-Bundesliga-Scores-and-Fixtures",
        "EFL Championship": "https://fbref.com/en/comps/10/{SEASON}/schedule/{SEASON}-Championship-Scores-and-Fixtures",
        "Major League Soccer": "https://fbref.com/en/comps/22/{SEASON}/schedule/{SEASON}-MLS-Scores-and-Fixtures",
    }

    @classmethod
    def get(cls, season: str, league: str) -> str:
        """Returns all formatted URLs for the given season."""
        return cls.BASE_URLS[league].format(SEASON=season)


class RANKING_URL:

    BASE_URLS = {
        "premier league": "https://en.wikipedia.org/wiki/{SEASON}_Premier_League",
        "la liga": "https://en.wikipedia.org/wiki/{SEASON}_La_Liga",
        "serie a": "https://en.wikipedia.org/wiki/{SEASON}_Serie_A",
        "ligue 1": "https://en.wikipedia.org/wiki/{SEASON}_Ligue_1",
        "bundesliga": "https://en.wikipedia.org/wiki/{SEASON}_Bundesliga",
    }

    @classmethod
    def get(cls, league: str) -> str:
        """Returns all formatted URLs for the given season."""
        if league.strip() not in cls.BASE_URLS:
            raise ValueError(
                f"League {league} not found. The Available Leagues are: {', '.join(cls.BASE_URLS.keys())}"
            )
        return cls.BASE_URLS[league]


class PLAYERS_URL:
    BASE_URLS = {
        "premier league": "https://www.worldfootball.net/{type}/eng-premier-league-{SEASON}/",
        "la liga": "https://www.worldfootball.net/{type}/esp-primera-division-{SEASON}/",
        "serie a": "https://www.worldfootball.net/{type}/ita-serie-a-{SEASON}/",
        "ligue 1": "https://www.worldfootball.net/{type}/fra-ligue-1-{SEASON}/",
        "bundesliga": "https://www.worldfootball.net/{type}/bundesliga-{SEASON}/",
    }
    DATA_TYPE = {
        "G": "scorer",
        "A": "assists",
    }

    @classmethod
    def get(cls, league: str, data_type: str) -> str:
        """Returns all formatted URLs for the given season."""
        if league not in cls.BASE_URLS:
            raise ValueError(
                f"League {league} not found. The Available Leagues are: {', '.join(cls.BASE_URLS.keys())}"
            )
        elif data_type not in ["G", "A"]:
            raise ValueError(
                f"Type {data_type} not found. The Available Types are: G, A"
            )
        return cls.BASE_URLS[league].replace("{type}", cls.DATA_TYPE[data_type.upper()])


class TRANSFERS_URL:
    BASE_URLS = {
        "premier league": "https://www.worldfootball.net/transfers/eng-premier-league-{SEASON}/",
        "la liga": "https://www.worldfootball.net/transfers/esp-primera-division-{SEASON}/",
        "serie a": "https://www.worldfootball.net/transfers/ita-serie-a-{SEASON}/",
        "ligue 1": "https://www.worldfootball.net/transfers/fra-ligue-1-{SEASON}/",
        "bundesliga": "https://www.worldfootball.net/transfers/bundesliga-{SEASON}/",
    }

    @classmethod
    def get(cls, league: str) -> str:
        """Returns all formatted URLs for the given season."""
        if league not in cls.BASE_URLS:
            raise ValueError(
                f"League {league} not found. The Available Leagues are: {', '.join(cls.BASE_URLS.keys()).title()}"
            )
        return cls.BASE_URLS[league]
