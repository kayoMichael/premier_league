from typing import Literal

from flask import Blueprint, g, jsonify, request, send_file
from werkzeug.utils import secure_filename

from premier_league.api.services.transfer_service import TransferService
from premier_league.api.utils.decorator import safe_file_cleanup

transfer_bp = Blueprint("transfers", __name__)


@transfer_bp.route("/all_teams", methods=["GET"])
def get_all_teams():
    """Get a list of all Premier League teams.

    This endpoint returns all teams in the Premier League for a given season.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        tuple: JSON response containing:
            - list: Array of team objects with team details
            - int: HTTP status code
    """
    season = request.args.get("season")
    league = request.args.get("league")

    response = TransferService().get_all_current_teams(league=league, season=season)
    return jsonify(response[0]), response[1]


@transfer_bp.route("/transfers/in", methods=["GET"])
def get_transfer_in_data():
    """Get incoming transfer data for a specific team.

    This endpoint returns all players transferred into the specified team.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        team (str, required): Team name or identifier
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        tuple: JSON response containing:
            - list: Array of transfer objects with player and transfer details
            - int: HTTP status code

    Error Responses:
        400: Missing team parameter - when team is not provided
    """
    season = request.args.get("season")
    team = request.args.get("team")
    league = request.args.get("league")
    if team is None:
        return {"error": "Missing team parameter"}, 400

    response = TransferService().get_transfer_in_data(
        team=team, season=season, league=league if league else "Premier League"
    )
    return jsonify(response[0]), response[1]


@transfer_bp.route("/transfers/out", methods=["GET"])
def get_transfer_out_data():
    """Get outgoing transfer data for a specific team.

    This endpoint returns all players transferred out from the specified team.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        team (str, required): Team name or identifier
        league (str, optional): Filter results by league (e.g., 'Premier league')

    Returns:
        tuple: JSON response containing:
            - list: Array of transfer objects with player and transfer details
            - int: HTTP status code

    Error Responses:
        400: Missing team parameter - when team is not provided
    """
    season = request.args.get("season")
    team = request.args.get("team")
    league = request.args.get("league")
    if team is None:
        return {"error": "Missing team parameter"}, 400
    response = TransferService().get_transfer_out_data(
        team=team, season=season, league=league if league else "Premier League"
    )
    return jsonify(response[0]), response[1]


@transfer_bp.route("/transfers/csv_file", methods=["GET"])
@safe_file_cleanup
def get_transfer_data_csv():
    """Export transfer data to a CSV file.

    This endpoint generates and returns a CSV file containing transfer data for a specific team.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        team (str, required): Team name or identifier
        filename (str, required): Name for the exported file (without extension)
        league (str, optional): Filter results by league (e.g., 'Premier league')
        transfer_type (str, optional): Type of transfers to include:
            - "in": Only incoming transfers
            - "out": Only outgoing transfers
            - "both": Both incoming and outgoing transfers (default)

    Returns:
        file: CSV file download response

    Error Responses:
        400: Missing team parameter - when team is not provided
        400: Missing filename parameter - when filename is not provided
        400: Invalid type parameter - when transfer_type is not "in", "out", or "both"
    """
    g.temp_state = {}
    season = request.args.get("season")
    team = request.args.get("team")
    file_name = request.args.get("filename")
    league = request.args.get("league")
    transfer_type: Literal["in", "both", "out"] | None = request.args.get(
        "transfer_type"
    )
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
    response = TransferService().transfer_csv(
        team=team,
        file_name=safe_filename,
        transfer_type=transfer_type,
        season=season,
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


@transfer_bp.route("/transfers/json_file", methods=["GET"])
@safe_file_cleanup
def get_transfer_data_json():
    """Export transfer data to a JSON file.

    This endpoint generates and returns a JSON file containing transfer data for a specific team.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        team (str, required): Team name or identifier
        filename (str, required): Name for the exported file (without extension)
        league (str, optional): Filter results by league (e.g., 'Premier league')
        transfer_type (str, optional): Type of transfers to include:
            - "in": Only incoming transfers
            - "out": Only outgoing transfers
            - "both": Both incoming and outgoing transfers (default)

    Returns:
        file: JSON file download response

    Error Responses:
        400: Missing team parameter - when team is not provided
        400: Missing filename parameter - when filename is not provided
        400: Invalid type parameter - when transfer_type is not "in", "out", or "both"
    """
    g.temp_state = {}
    season = request.args.get("season")
    team = request.args.get("team")
    file_name = request.args.get("filename")
    league = request.args.get("league")
    transfer_type: Literal["in", "both", "out"] | None = request.args.get(
        "transfer_type"
    )
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
    response = TransferService().transfer_json(
        team=team,
        file_name=safe_filename,
        transfer_type=transfer_type,
        season=season,
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
