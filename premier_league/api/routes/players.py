from flask import Blueprint, g, jsonify, request, send_file
from werkzeug.utils import secure_filename

from premier_league.api.services.player_service import PlayerService
from premier_league.api.utils.decorator import safe_file_cleanup

players_bp = Blueprint("players", __name__)


@players_bp.route("/players/goals", methods=["GET"])
def get_scorers():
    """Get a list of top goalscorers.

    This endpoint returns player statistics sorted by goals scored.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        limit (int, optional): Maximum number of results to return
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        tuple: JSON response containing:
            - list: Array of player objects with scoring statistics
            - int: HTTP status code

    Error Responses:
        400: Invalid limit parameter - when limit is not a number
    """
    season = request.args.get("season")
    limit = request.args.get("limit")
    league = request.args.get("league")
    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400

    response = PlayerService().get_player_data_goals(
        season=season,
        limit=int(limit) if limit else None,
        league=league if league else "Premier League",
    )
    return jsonify(response[0]), response[1]


@players_bp.route("/players/assists", methods=["GET"])
def get_assists():
    """Get a list of top assist providers.

    This endpoint returns player statistics sorted by assists provided.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        limit (int, optional): Maximum number of results to return
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        tuple: JSON response containing:
            - list: Array of player objects with assist statistics
            - int: HTTP status code

    Error Responses:
        400: Invalid limit parameter - when limit is not a number
    """
    season = request.args.get("season")
    limit = request.args.get("limit")
    league = request.args.get("league")
    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400

    response = PlayerService().get_player_data_assists(
        season=season,
        limit=int(limit) if limit else None,
        league=league if league else "Premier League",
    )
    return jsonify(response[0]), response[1]


@players_bp.route("/players/goals/csv_file", methods=["GET"])
@safe_file_cleanup
def get_scorers_csv():
    """Export top goalscorers data to a CSV file.

    This endpoint generates and returns a CSV file containing goal scoring statistics.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        filename (str, required): Name for the exported file (without extension)
        header (str, optional): Include header row in CSV if provided
        limit (int, optional): Maximum number of results to return
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        file: CSV file download response

    Error Responses:
        400: Invalid limit parameter - when limit is not a number
        400: Missing filename parameter - when filename is not provided
    """
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")
    league = request.args.get("league")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_goals_csv(
        file_name=safe_filename,
        season=season,
        header=header,
        limit=int(limit) if limit else None,
        league=league if league else "Premier League",
    )
    g.temp_state["file_path"] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(
            file_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"{safe_filename}.csv",
        )

    return jsonify(response[0]), response[1]


@players_bp.route("/players/assists/csv_file", methods=["GET"])
@safe_file_cleanup
def get_assists_csv():
    """Export top assist providers data to a CSV file.

    This endpoint generates and returns a CSV file containing assist statistics.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        filename (str, required): Name for the exported file (without extension)
        header (str, optional): Include header row in CSV if provided
        limit (int, optional): Maximum number of results to return
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        file: CSV file download response

    Error Responses:
        400: Invalid limit parameter - when limit is not a number
        400: Missing filename parameter - when filename is not provided
    """
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")
    league = request.args.get("league")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_assists_csv(
        file_name=safe_filename,
        season=season,
        header=header,
        limit=int(limit) if limit else None,
        league=league if league else "Premier League",
    )
    g.temp_state["file_path"] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(
            file_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"{safe_filename}.csv",
        )

    return jsonify(response[0]), response[1]


@players_bp.route("/players/goals/json_file", methods=["GET"])
@safe_file_cleanup
def get_scorers_json():
    """Export top goalscorers data to a JSON file.

    This endpoint generates and returns a JSON file containing goal scoring statistics.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        filename (str, required): Name for the exported file (without extension)
        header (str, optional): Include metadata in JSON if provided
        limit (int, optional): Maximum number of results to return
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        file: JSON file download response

    Error Responses:
        400: Invalid limit parameter - when limit is not a number
        400: Missing filename parameter - when filename is not provided
    """
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")
    league = request.args.get("league")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_goals_json(
        file_name=safe_filename,
        season=season,
        header=header,
        limit=int(limit) if limit else None,
        league=league if league else "Premier League",
    )
    g.temp_state["file_path"] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(
            file_path,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"{safe_filename}.json",
        )

    return jsonify(response[0]), response[1]


@players_bp.route("/players/assists/json_file", methods=["GET"])
@safe_file_cleanup
def get_assists_json():
    """Export top assist providers data to a JSON file.

    This endpoint generates and returns a JSON file containing assist statistics.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        filename (str, required): Name for the exported file (without extension)
        header (str, optional): Include metadata in JSON if provided
        limit (int, optional): Maximum number of results to return
        league (str, optional): Filter results by league (e.g., 'Premier league

    Returns:
        file: JSON file download response

    Error Responses:
        400: Invalid limit parameter - when limit is not a number
        400: Missing filename parameter - when filename is not provided
    """
    g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    header = request.args.get("header")
    limit = request.args.get("limit")
    league = request.args.get("league")

    if limit and not limit.isdigit():
        return {"error": "Limit must be a number"}, 400
    elif file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = PlayerService().get_player_data_assists_json(
        file_name=safe_filename,
        season=season,
        header=header,
        limit=int(limit) if limit else None,
        league=league if league else "Premier League",
    )
    g.temp_state["file_path"] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(
            file_path,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"{safe_filename}.json",
        )

    return jsonify(response[0]), response[1]
