class PredictorURL:
    BASE_URLS = {
        "PREM": "https://fbref.com/en/comps/9/{SEASON}/schedule/{SEASON}-Premier-League-Scores-and-Fixtures",
        "LA_LIGA": "https://fbref.com/en/comps/12/{SEASON}/schedule/{SEASON}-La-Liga-Scores-and-Fixtures",
        "SERIE_A": "https://fbref.com/en/comps/11/{SEASON}/schedule/{SEASON}-Serie-A-Scores-and-Fixtures",
        "LEAGUE_1": "https://fbref.com/en/comps/13/{SEASON}/schedule/{SEASON}-League-1-Scores-and-Fixtures",
        "BUNDESLIGA": "https://fbref.com/en/comps/20/{SEASON}/schedule/{SEASON}-Bundesliga-Scores-and-Fixtures",
        "EFL_CHAMPIONSHIP": "https://fbref.com/en/comps/10/{SEASON}/schedule/{SEASON}-Championship-Scores-and-Fixtures",
    }

    @classmethod
    def get_all(cls, season: str):
        """Returns all formatted URLs for the given season."""
        return [url.format(SEASON=season) for url in cls.BASE_URLS.values()]

