import os

from premier_league import RankingTable


class RankingService:

    @staticmethod
    def get_premier_league_ranking(
        season: str = None, header: str = None, league: str = None
    ):
        try:
            json_data = RankingTable(season, league).get_ranking_dict(header)
        except ValueError as e:
            return {"error": str(e)}, 400
        print(json_data)
        return json_data, 200

    @staticmethod
    def get_premier_league_ranking_list(season: str = None, league: str = None):
        try:
            ranking_data = RankingTable(season, league).get_ranking_list()
        except ValueError as e:
            return {"error": str(e)}, 400

        return ranking_data, 200

    @staticmethod
    def get_premier_league_ranking_csv(
        file_name: str, season: str = None, league: str = None
    ):
        try:
            RankingTable(season, league).get_ranking_csv(file_name)
        except ValueError as e:
            return {"error": str(e)}, 400
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        file_directory = os.path.join(project_root, "files", f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def get_premier_league_ranking_json(
        file_name: str, season: str = None, league: str = None
    ):
        try:
            RankingTable(season, league).get_ranking_json(file_name)
        except ValueError as e:
            return {"error": str(e)}, 400
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        file_directory = os.path.join(project_root, "files", f"{file_name}.json")
        return file_directory, 200

    @staticmethod
    def get_premier_league_ranking_pdf(
        file_name: str, season: str = None, league: str = None
    ):
        try:
            RankingTable(season, league).get_ranking_pdf(file_name)
        except ValueError as e:
            return {"error": str(e)}, 400
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        file_directory = os.path.join(project_root, "files", f"{file_name}.pdf")
        return file_directory, 200
