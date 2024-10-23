from flask import Blueprint, jsonify, request, send_file, g
from app.services.transfer_service import TransferService
from werkzeug.utils import secure_filename
from app.utils.decorator import safe_file_cleanup
from typing import Literal

transfer_bp = Blueprint('transfers', __name__)


@transfer_bp.route('/all_teams', methods=['GET'])
def get_all_teams():
    season = request.args.get("season")
    response = TransferService().get_all_current_teams(season)
    return jsonify(response[0]), response[1]


@transfer_bp.route('/transfers/in', methods=['GET'])
def get_transfer_in_data():
    season = request.args.get("season")
    team = request.args.get("team")
    if team is None:
        return {"error": "Missing team parameter"}, 400
    response = TransferService().get_transfer_in_data(team, season=season)
    return jsonify(response[0]), response[1]


@transfer_bp.route('/transfers/out', methods=['GET'])
def get_transfer_out_data():
    season = request.args.get("season")
    team = request.args.get("team")
    if team is None:
        return {"error": "Missing team parameter"}, 400
    response = TransferService().get_transfer_out_data(team, season=season)
    return jsonify(response[0]), response[1]


@transfer_bp.route('/transfers/csv_file', methods=['GET'])
@safe_file_cleanup
def get_transfer_data_csv():
    g.temp_state = {}
    season = request.args.get("season")
    team = request.args.get("team")
    file_name = request.args.get("filename")
    transfer_type: Literal["in", "both", "out"] | None = request.args.get("transfer_type")
    if team is None:
        return {"error": "Missing team parameter"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400
    elif transfer_type and transfer_type not in ["in", "out", "both"]:
        return {"error": "Invalid type parameter"}, 400
    if transfer_type is None:
        transfer_type: Literal["in", "both", "out"] = "both"

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = TransferService().transfer_csv(team, safe_filename, transfer_type, season)
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'{safe_filename}.csv'
                         )
    return jsonify(response[0]), response[1]

@transfer_bp.route('/transfers/json_file', methods=['GET'])
@safe_file_cleanup
def get_transfer_data_json():
    g.temp_state = {}
    season = request.args.get("season")
    team = request.args.get("team")
    file_name = request.args.get("filename")
    transfer_type: Literal["in", "both", "out"] | None = request.args.get("transfer_type")
    if team is None:
        return {"error": "Missing team parameter"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400
    elif transfer_type and transfer_type not in ["in", "out", "both"]:
        return {"error": "Invalid type parameter"}, 400
    if transfer_type is None:
        transfer_type: Literal["in", "both", "out"] = "both"

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = TransferService().transfer_json(team, safe_filename, transfer_type, season)
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='application/json',
                         as_attachment=True,
                         download_name=f'{safe_filename}.json'
                         )
    return jsonify(response[0]), response[1]
