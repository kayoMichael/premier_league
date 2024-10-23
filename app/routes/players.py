from flask import Blueprint, jsonify, request, send_file, g
from app.services.player_service import PlayerService
from werkzeug.utils import secure_filename

from app.utils.decorator import safe_file_cleanup

players_bp = Blueprint('players', __name__)


@players_bp.route('/players/goals', methods=['GET'])
def get_scorers():
    season = request.args.get("season")
    limit = request.args.get("limit")
    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400

    response = PlayerService().get_player_data_goals(season=season, limit=int(limit))
    return jsonify(response[0]), response[1]


@players_bp.route('/players/assists', methods=['GET'])
def get_assists():
    season = request.args.get("season")
    limit = request.args.get("limit")
    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400

    response = PlayerService().get_player_data_assists(season=season, limit=int(limit))
    return jsonify(response[0]), response[1]


@players_bp.route('/players/goals/csv_file', methods=['GET'])
@safe_file_cleanup
def get_scorers_csv():
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_goals_csv(safe_filename, season=season, header=header, limit=int(limit))
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'{safe_filename}.csv'
                         )

    return jsonify(response[0]), response[1]


@players_bp.route('/players/assists/csv_file', methods=['GET'])
@safe_file_cleanup
def get_assists_csv():
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_assists_csv(safe_filename, season=season, header=header, limit=int(limit))
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'{safe_filename}.csv'
                         )

    return jsonify(response[0]), response[1]


@players_bp.route('/players/goals/json_file', methods=['GET'])
@safe_file_cleanup
def get_scorers_json():
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_goals_json(safe_filename, season=season, header=header, limit=int(limit))
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='application/json',
                         as_attachment=True,
                         download_name=f'{safe_filename}.json'
                         )

    return jsonify(response[0]), response[1]


@players_bp.route('/players/assists/json_file', methods=['GET'])
@safe_file_cleanup
def get_assists_json():
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_assists_json(safe_filename, season=season, header=header, limit=int(limit))
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='application/json',
                         as_attachment=True,
                         download_name=f'{safe_filename}.json'
                         )

    return jsonify(response[0]), response[1]
