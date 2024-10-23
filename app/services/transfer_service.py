from premier_league import Transfers
from premier_league.players.transfers import TeamNotFoundError
from typing import Literal
import os


class TransferService:

    @staticmethod
    def get_all_current_teams(season: str = None):
        try:
            all_teams = Transfers(season).get_all_current_teams()
        except ValueError as e:
            return {"error": str(e)}, 400

        return all_teams, 200

    @staticmethod
    def get_transfer_in_data(team: str, season: str = None):
        try:
            transfer_data = Transfers(season).transfer_in_table(team)
        except ValueError as e:
            return {"error": str(e)}, 400

        return transfer_data, 200

    @staticmethod
    def get_transfer_out_data(team: str, season: str = None):
        try:
            transfer_data = Transfers(season).transfer_out_table(team)
        except TeamNotFoundError:
            return {"error": f"No Team by the name of {team} exists in the {season} Premier league Season. For all teams in the {season} please invoke /all_teams."}, 400

        return transfer_data, 200

    @staticmethod
    def transfer_csv(team: str, file_name: str, transfer_type: Literal["in", "out", "both"], season: str = None):
        try:
            Transfers(season).transfer_csv(team, file_name, transfer_type)
        except TeamNotFoundError:
            return {"error": f"No Team by the name of {team} exists in the {season} Premier league Season. For all teams in the {season} please invoke /all_teams."}, 400

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        file_directory = os.path.join(project_root, 'files', f"{file_name}.csv")
        return file_directory, 200

    @staticmethod
    def transfer_json(team: str, file_name: str, transfer_type: Literal["in", "out", "both"] = "both", season: str = None):
        try:
            Transfers(season).transfer_json(team, file_name, transfer_type)
        except TeamNotFoundError:
            return {"error": f"No Team by the name of {team} exists in the {season} Premier league Season. For all teams in the {season} please invoke /all_teams."}, 400

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        file_directory = os.path.join(project_root, 'files', f"{file_name}.json")
        return file_directory, 200
