import os
from typing import Literal

from ...utils.methods import export_to_dict


class TransferService:
    @staticmethod
    def get_all_current_teams(league: str, season: str = None):
        from premier_league import Transfers

        try:
            all_teams = Transfers(season, league).get_all_current_teams()
        except ValueError as e:
            return {"error": str(e)}, 400

        return all_teams, 200

    @staticmethod
    def get_transfer_in_data(team: str, league: str, season: str = None):
        from premier_league import TeamNotFoundError, Transfers

        try:
            transfer_data = Transfers(season, league).transfer_in_table(team)
        except ValueError as e:
            return {"error": str(e)}, 400
        except TeamNotFoundError:
            return {
                "error": f"No Team by the name of {team} exists in the {season} {league} Season. For all teams in the {season} season, please invoke /all_teams."
            }, 404

        return export_to_dict(transfer_data), 200

    @staticmethod
    def get_transfer_out_data(team: str, league: str, season: str = None):
        from premier_league import Transfers
        from premier_league.transfers.transfers import TeamNotFoundError

        try:
            transfer_data = Transfers(season, league).transfer_out_table(team)
        except TeamNotFoundError:
            return {
                "error": f"No Team by the name of {team} exists in the {season} {league} Season. For all teams in the {season} season, please invoke /all_teams."
            }, 404

        return export_to_dict(transfer_data), 200

    @staticmethod
    def transfer_csv(
        team: str,
        file_name: str,
        transfer_type: Literal["in", "out", "both"],
        league: str,
        season: str = None,
    ):
        from premier_league import Transfers
        from premier_league.transfers.transfers import TeamNotFoundError

        try:
            Transfers(season, league).transfer_csv(team, file_name, transfer_type)
        except TeamNotFoundError:
            return {
                "error": f"No Team by the name of {team} exists in the {season} {league} Season. For all teams in the {season} season, please invoke /all_teams."
            }, 404

        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def transfer_json(
        team: str,
        file_name: str,
        transfer_type: Literal["in", "out", "both"],
        league: str,
        season: str = None,
    ):
        from premier_league import Transfers
        from premier_league.transfers.transfers import TeamNotFoundError

        try:
            Transfers(season, league).transfer_json(team, file_name, transfer_type)
        except TeamNotFoundError:
            return {
                "error": f"No Team by the name of {team} exists in the {season} {league} Season. For all teams in the {season} season, please invoke /all_teams."
            }, 404

        file_directory = os.path.join(os.getcwd(), "files", f"{file_name}.json")
        return file_directory, 200
