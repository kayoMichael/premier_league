from premier_league import RankingTable
from utils.methods import (
    export_to_csv,
    export_to_json,
    generate_http_response,
    save_to_s3,
)
import os

S3_NAME = os.getenv("S3_BUCKET_NAME")


class RankingLambda(RankingTable):
    def __init__(self, path, season=None, filename=None, header=None):
        super().__init__(season)
        self.filename = filename
        self.path = path
        self.header = header

    def handle_request(self):
        if self.path == "/ranking":
            return self.get_prem_ranking_list()
        elif self.path == "/ranking_csv":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            export_to_csv(
                self.filename, self.get_prem_ranking_list(), header=self.header
            )
            return generate_http_response(
                200, save_to_s3(f"{self.filename}.csv", S3_NAME)
            )
        elif self.path == "/ranking_json":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            export_to_json(
                self.filename, self.get_prem_ranking_list(), header_1=self.header
            )
            return generate_http_response(
                200, save_to_s3(f"{self.filename}.json", S3_NAME)
            )
        elif self.path == "/ranking_pdf":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            self.get_prem_ranking_pdf(self.filename, "tmp")
            return generate_http_response(
                200, save_to_s3(f"{self.filename}.pdf", S3_NAME)
            )


def lambda_handler(event, _):
    season = event["queryStringParameters"].get("season")
    filename = event["queryStringParameters"].get("filename")
    header = event["queryStringParameters"].get("header")

    try:
        player = RankingLambda(event["path"], season, filename, header)
        return player.handle_request()
    except Exception as e:
        return generate_http_response(500, str(e))
