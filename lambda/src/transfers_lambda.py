from premier_league import Transfers
import json
from utils.methods import export_to_csv, export_to_json
import uuid
import boto3
import os

s3 = boto3.client('s3')
S3_NAME = os.getenv('S3_BUCKET_NAME')


class HandleLambdaRequest(Transfers):
    def __init__(self, path, team, season=None, filename=None, export_type=None):
        super().__init__(target_season=season)
        self.path = path
        self.target_team = team
        self.filename = filename
        self.export_type = export_type

    def handle_request(self):
        if self.path == "/transfers_in":
            return self.transfer_in_table(self.target_team)
        elif self.path == "/transfers_out":
            return self.transfer_out_table(self.target_team)
        elif self.path == "/transfers_csv":
            if self.filename is None:
                return generate_http_response("Filename is required", 400)
            elif self.export_type not in ["in", "out", "both"]:
                return generate_http_response("Export type is invalid or missing. It must be either in, out or both", 400)
            if self.export_type == "both":
                export_to_csv(self.filename, self.transfer_in_table(self.target_team), self.transfer_out_table(self.target_team),
                              f"{self.season} {self.target_team} Transfers In", "{self.season} {self.target_team} Transfers Out")
            elif self.export_type == "in":
                export_to_csv(self.filename, self.transfer_in_table(self.target_team), header=f"{self.season} {self.target_team} Transfers In")
            elif self.export_type == "out":
                export_to_csv(self.filename, self.transfer_out_table(self.target_team), header=f"{self.season} {self.target_team} Transfers Out")

            return generate_http_response(self.save_to_s3(f"{self.filename}.csv"), 200)
        elif self.path == "/transfers_json":
            if self.filename is None:
                return generate_http_response("Filename is required", 400)
            elif self.export_type not in ["in", "out", "both"]:
                return generate_http_response("Export type is invalid or missing. It must be either in, out or both", 400)

            if self.export_type == "both":
                export_to_json(self.filename, self.transfer_in_table(self.target_team), self.transfer_out_table(self.target_team),
                               f"{self.season} {self.target_team} Transfers In", "{self.season} {self.target_team} Transfers Out")
            elif self.export_type == "in":
                export_to_json(self.filename, self.transfer_in_table(self.target_team), header_1=f"{self.season} {self.target_team} Transfers In")
            elif self.export_type == "out":
                export_to_json(self.filename, self.transfer_out_table(self.target_team), header_1=f"{self.season} {self.target_team} Transfers Out")

            return generate_http_response(self.save_to_s3(f"{self.filename}.json"), 200)

    @staticmethod
    def save_to_s3(file_name):
        s3_directory = uuid.uuid4()
        s3_file_path = f"{s3_directory}/{file_name}"
        s3.upload_file(f"tmp/{file_name}", 'premier-league-transfers', s3_file_path)

        return s3_file_path


def generate_http_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }


def lambda_handler(event, _):
    season = event['queryStringParameters'].get('season')
    team = event['queryStringParameters'].get('team')
    filename = event['queryStringParameters'].get('filename')
    export_type = event['queryStringParameters'].get('export_type')

    if team is None:
        return generate_http_response("Team is required", 400)

    try:
        response = HandleLambdaRequest(event['path'], team, season, filename, export_type).handle_request()
    except Exception as e:
        return generate_http_response(str(e), 400)

    return response