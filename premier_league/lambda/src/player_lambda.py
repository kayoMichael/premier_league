from premier_league import PlayerSeasonLeaders
from utils.methods import export_to_csv, export_to_json, generate_http_response, save_to_s3
import os

S3_NAME = os.getenv('S3_BUCKET_NAME')


class PlayerLambda(PlayerSeasonLeaders):
    def __init__(self, path, stat_type, season=None, filename=None, limit=None, header=None):
        super().__init__(stat_type, season)
        self.filename = filename
        self.path = path
        self.limit = limit
        self.header = header

    def handle_request(self):
        if self.path == "/player_ranking":
            return self.get_top_stats_list(self.limit)
        elif self.path == "/player_csv":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            export_to_csv(self.filename, self.get_top_stats_list(self.limit), header=self.header)
            return generate_http_response(200, save_to_s3(f"{self.filename}.csv", S3_NAME))
        elif self.path == "/player_json":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            export_to_json(self.filename, self.get_top_stats_list(self.limit), header_1=self.header)
            return generate_http_response(200, save_to_s3(f"{self.filename}.json", S3_NAME))
        elif self.path == "/player_pdf":
            if self.filename is None:
                return generate_http_response(400, "Filename is required")
            self.get_top_stats_pdf(self.filename, "tmp")
            return generate_http_response(200, save_to_s3(f"{self.filename}.pdf", S3_NAME))


def lambda_handler(event, _):
    season = event['queryStringParameters'].get('season')
    stat_type = event['queryStringParameters'].get('stat_type')
    filename = event['queryStringParameters'].get('filename')
    limit = event['queryStringParameters'].get('limit')
    header = event['queryStringParameters'].get('header')
    if stat_type != "G" or stat_type != "A":
        return generate_http_response(400, "Invalid stat type")

    try:
        player = PlayerLambda(event['path'], season, stat_type, filename, limit, header)
        return player.handle_request()
    except Exception as e:
        return generate_http_response(500, str(e))
