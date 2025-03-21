import os


class RankingService:
    @staticmethod
    def get_ranking(league: str, season: str = None, header: str = None):
        from premier_league import RankingTable

        try:
            json_data = RankingTable(league, season).get_ranking_dict(header)
        except ValueError as e:
            return {"error": str(e)}, 400
        return json_data, 200

    @staticmethod
    def get_ranking_list(league: str, season: str = None):
        from premier_league import RankingTable

        try:
            ranking_data = RankingTable(league, season).get_ranking_list()
        except ValueError as e:
            return {"error": str(e)}, 400

        return ranking_data, 200

    @staticmethod
    def get_ranking_csv(file_name: str, league: str, season: str = None):
        from premier_league import RankingTable

        try:
            RankingTable(league, season).get_ranking_csv(file_name)
        except ValueError as e:
            return {"error": str(e)}, 400
        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def get_ranking_json(file_name: str, league: str, season: str = None):
        from premier_league import RankingTable

        try:
            RankingTable(league, season).get_ranking_json(file_name)
        except ValueError as e:
            return {"error": str(e)}, 400
        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.json")
        return file_directory, 200

    @staticmethod
    def get_ranking_pdf(file_name: str, league: str, season: str = None):
        from premier_league import RankingTable

        try:
            RankingTable(league, season).get_ranking_pdf(file_name)
        except ValueError as e:
            return {"error": str(e)}, 400
        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.pdf")
        return file_directory, 200
