import os


class PlayerService:
    @staticmethod
    def get_player_data_goals(
        season: str = None, limit: int = None, league: str = None
    ):
        from premier_league import PlayerSeasonLeaders
        try:
            player_data = PlayerSeasonLeaders("G", season, league).get_top_stats_list(
                limit=limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        return player_data, 200

    @staticmethod
    def get_player_data_assists(
        season: str = None, limit: int = None, league: str = None
    ):
        from premier_league import PlayerSeasonLeaders
        try:
            player_data = PlayerSeasonLeaders("A", season, league).get_top_stats_list(
                limit=limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        return player_data, 200

    @staticmethod
    def get_player_data_goals_csv(
        file_name: str,
        season: str = None,
        header: str = None,
        limit: int = None,
        league: str = None,
    ):
        from premier_league import PlayerSeasonLeaders
        try:
            PlayerSeasonLeaders("G", season, league).get_top_stats_csv(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        file_directory = os.path.join(project_root, "files", f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def get_player_data_assists_csv(
        file_name: str,
        season: str = None,
        header: str = None,
        limit: int = None,
        league: str = None,
    ):
        from premier_league import PlayerSeasonLeaders
        try:
            PlayerSeasonLeaders("A", season, league).get_top_stats_csv(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        file_directory = os.path.join(project_root, "files", f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def get_player_data_goals_json(
        file_name: str,
        season: str = None,
        header: str = None,
        limit: int = None,
        league: str = None,
    ):
        from premier_league import PlayerSeasonLeaders
        try:
            PlayerSeasonLeaders("G", season, league).get_top_stats_json(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        file_directory = os.path.join(project_root, "files", f"{file_name}.json")
        return file_directory, 200

    @staticmethod
    def get_player_data_assists_json(
        file_name: str,
        season: str = None,
        header: str = None,
        limit: int = None,
        league: str = None,
    ):
        from premier_league import PlayerSeasonLeaders
        try:
            PlayerSeasonLeaders("A", season, league).get_top_stats_json(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        file_directory = os.path.join(project_root, "files", f"{file_name}.json")
        return file_directory, 200
