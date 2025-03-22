import os

from transfers.transfers import Transfers

from .utils.methods import (
    export_to_csv,
    export_to_json,
    generate_http_response,
    save_to_s3,
)

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


class HandleLambdaRequest(Transfers):
    def __init__(
        self,
        path,
        team,
        season=None,
        filename=None,
        export_type=None,
        league=None,
    ):
        super().__init__(target_season=season, league=league)
        self.path = path
        self.target_team = team
        self.filename = filename
        self.export_type = export_type
        self.s3_name = (S3_BUCKET_NAME,)

    def handle_request(self):
        if self.path == "/transfers_in":
            return self.transfer_in_table(self.target_team)
        elif self.path == "/transfers_out":
            return self.transfer_out_table(self.target_team)
        elif self.path == "/transfers_csv":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            elif self.export_type not in ["in", "out", "both"]:
                return generate_http_response(
                    400,
                    "Export type is invalid or missing. It must be either in, out or both",
                )
            if self.export_type == "both":
                export_to_csv(
                    self.filename,
                    self.transfer_in_table(self.target_team),
                    self.transfer_out_table(self.target_team),
                    f"{self.season} {self.target_team} Transfers In",
                    "{self.season} {self.target_team} Transfers Out",
                )
            elif self.export_type == "in":
                export_to_csv(
                    self.filename,
                    self.transfer_in_table(self.target_team),
                    header=f"{self.season} {self.target_team} Transfers In",
                )
            elif self.export_type == "out":
                export_to_csv(
                    self.filename,
                    self.transfer_out_table(self.target_team),
                    header=f"{self.season} {self.target_team} Transfers Out",
                )
            return generate_http_response(
                200, save_to_s3(f"{self.filename}.csv", self.s3_name)
            )
        elif self.path == "/transfers_json":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            elif self.export_type not in ["in", "out", "both"]:
                return generate_http_response(
                    400,
                    "Export type is invalid or missing. It must be either in, out or both",
                )

            if self.export_type == "both":
                export_to_json(
                    self.filename,
                    self.transfer_in_table(self.target_team),
                    self.transfer_out_table(self.target_team),
                    f"{self.season} {self.target_team} Transfers In",
                    "{self.season} {self.target_team} Transfers Out",
                )
            elif self.export_type == "in":
                export_to_json(
                    self.filename,
                    self.transfer_in_table(self.target_team),
                    header_1=f"{self.season} {self.target_team} Transfers In",
                )
            elif self.export_type == "out":
                export_to_json(
                    self.filename,
                    self.transfer_out_table(self.target_team),
                    header_1=f"{self.season} {self.target_team} Transfers Out",
                )

            return generate_http_response(
                200, save_to_s3(f"{self.filename}.json", self.s3_name)
            )


def lambda_handler(event, _):
    season = event["queryStringParameters"].get("season")
    team = event["queryStringParameters"].get("team")
    filename = event["queryStringParameters"].get("filename")
    export_type = event["queryStringParameters"].get("export_type")
    league = event["queryStringParameters"].get("league")

    if team is None:
        return generate_http_response(400, "Team is required")

    try:
        response = HandleLambdaRequest(
            event["path"], team, season, filename, export_type, league
        ).handle_request()
    except Exception as e:
        return generate_http_response(400, str(e))

    return response
