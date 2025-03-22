import os

from ...utils.methods import export_to_dict


class PlayerService:
    @staticmethod
    def get_player_data_goals(league: str, season: str = None, limit: int = None):
        from premier_league import PlayerSeasonLeaders

        try:
            player_data = PlayerSeasonLeaders("G", season, league).get_top_stats_list(
                limit=limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        return export_to_dict(player_data), 200

    @staticmethod
    def get_player_data_assists(league: str, season: str = None, limit: int = None):
        from premier_league import PlayerSeasonLeaders

        try:
            player_data = PlayerSeasonLeaders("A", season, league).get_top_stats_list(
                limit=limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        return export_to_dict(player_data), 200

    @staticmethod
    def get_player_data_goals_csv(
        file_name: str,
        league: str,
        season: str = None,
        header: str = None,
        limit: int = None,
    ):
        from premier_league import PlayerSeasonLeaders

        try:
            PlayerSeasonLeaders("G", season, league).get_top_stats_csv(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def get_player_data_assists_csv(
        file_name: str,
        league: str,
        season: str = None,
        header: str = None,
        limit: int = None,
    ):
        from premier_league import PlayerSeasonLeaders

        try:
            PlayerSeasonLeaders("A", season, league).get_top_stats_csv(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def get_player_data_goals_json(
        file_name: str,
        league: str,
        season: str = None,
        header: str = None,
        limit: int = None,
    ):
        from premier_league import PlayerSeasonLeaders

        try:
            PlayerSeasonLeaders("G", season, league).get_top_stats_json(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.json")
        return file_directory, 200

    @staticmethod
    def get_player_data_assists_json(
        file_name: str,
        league: str,
        season: str = None,
        header: str = None,
        limit: int = None,
    ):
        from premier_league import PlayerSeasonLeaders

        try:
            PlayerSeasonLeaders("A", season, league).get_top_stats_json(
                file_name, header, limit
            )
        except ValueError as e:
            return {"error": str(e)}, 400

        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.json")
        return file_directory, 200
