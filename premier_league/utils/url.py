from datetime import datetime


class PredictorURL:
    BASE_URLS = {
        "premier league": "https://fbref.com/en/comps/9/{SEASON}/schedule/{SEASON}-Premier-League-Scores-and-Fixtures",
        "la liga": "https://fbref.com/en/comps/12/{SEASON}/schedule/{SEASON}-La-Liga-Scores-and-Fixtures",
        "serie a": "https://fbref.com/en/comps/11/{SEASON}/schedule/{SEASON}-Serie-A-Scores-and-Fixtures",
        "ligue 1": "https://fbref.com/en/comps/13/{SEASON}/schedule/{SEASON}-League-1-Scores-and-Fixtures",
        "fußball-bundesliga": "https://fbref.com/en/comps/20/{SEASON}/schedule/{SEASON}-Bundesliga-Scores-and-Fixtures",
        "efl championship": "https://fbref.com/en/comps/10/{SEASON}/schedule/{SEASON}-Championship-Scores-and-Fixtures",
    }

    @classmethod
    def get(cls, season: str, league: str) -> str:
        """Returns all formatted URLs for the given season."""
        if league.lower() not in cls.BASE_URLS:
            raise ValueError(
                f"League {league} not found. The Available Leagues are: {', '.join(cls.BASE_URLS.keys())}"
            )
        return cls.BASE_URLS[league.lower()].format(SEASON=season)


class RANKING_URL:
    BASE_URLS = {
        "premier league": {
            1992: "https://en.wikipedia.org/wiki/{SEASON}_Premier_League",
            1947: "https://en.wikipedia.org/wiki/{SEASON}_Football_League_First_Division",
        },
        "la liga": {1929: "https://en.wikipedia.org/wiki/{SEASON}_La_Liga"},
        "serie a": {1929: "https://en.wikipedia.org/wiki/{SEASON}_Serie_A"},
        "ligue 1": {
            2002: "https://en.wikipedia.org/wiki/{SEASON}_Ligue_1",
            1945: "https://en.wikipedia.org/wiki/{SEASON}_French_Division_1",
        },
        "bundesliga": {1963: "https://en.wikipedia.org/wiki/{SEASON}_Bundesliga"},
    }

    @classmethod
    def get(cls, league: str, target_season: str) -> str:
        """Returns all formatted URLs for the given season."""
        league = league.strip()
        if league not in cls.BASE_URLS:
            raise ValueError(
                f"League {league} not found. The Available Leagues are: {', '.join(cls.BASE_URLS.keys())}"
            )
        if target_season[0:4].isdigit():
            target_season = int(target_season[0:4])
            if target_season > datetime.now().year:
                raise ValueError("Season should be in the past")

            seasons = cls.BASE_URLS[league].keys()
            if min(seasons) > target_season:
                raise ValueError(
                    f"Class Does not Support Season that is less than {min(seasons)}"
                )
            if 1939 <= target_season <= 1945:
                raise ValueError("Class Does not Support WWII soccer seasons.")
            for season in seasons:
                if target_season >= season:
                    return cls.BASE_URLS[league][season]
        else:
            raise ValueError("Season should be in the format 'YYYY-YYYY'")


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
