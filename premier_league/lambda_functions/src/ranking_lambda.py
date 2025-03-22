import os

from ranking.ranking_table import RankingTable

from .utils.methods import (
    export_to_csv,
    export_to_json,
    generate_http_response,
    save_to_s3,
)

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


class RankingLambda(RankingTable):
    def __init__(
        self,
        path,
        season,
        filename,
        header,
        league=None,
    ):
        super().__init__(league, season)
        self.filename = filename
        self.path = path
        self.header = header
        self.s3_name = (S3_BUCKET_NAME,)

    def handle_request(self):
        if self.path == "/ranking":
            return self.get_ranking_list()
        elif self.path == "/ranking_csv":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            export_to_csv(self.filename, self.get_ranking_list(), header=self.header)
            return generate_http_response(
                200, save_to_s3(f"{self.filename}.csv", self.s3_name)
            )
        elif self.path == "/ranking_json":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            export_to_json(self.filename, self.get_ranking_list(), header_1=self.header)
            return generate_http_response(
                200, save_to_s3(f"{self.filename}.json", self.s3_name)
            )
        elif self.path == "/ranking_pdf":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            self.get_ranking_pdf(self.filename, "tmp")
            return generate_http_response(
                200, save_to_s3(f"{self.filename}.pdf", self.s3_name)
            )


def lambda_handler(event, _):
    season = event["queryStringParameters"].get("season")
    filename = event["queryStringParameters"].get("filename")
    header = event["queryStringParameters"].get("header")
    league = event["queryStringParameters"].get("league")

    try:
        player = RankingLambda(event["path"], season, filename, header, league)
        return player.handle_request()
    except Exception as e:
        return generate_http_response(500, str(e))
