from flask import Blueprint, jsonify, request, send_file, g
from premier_league.api.services.ranking_service import RankingService
from werkzeug.utils import secure_filename
from premier_league.api.utils.decorator import safe_file_cleanup

ranking_bp = Blueprint('ranking', __name__)


@ranking_bp.route('/ranking', methods=['GET'])
def get_standings():
    """Get the Premier League standings with detailed statistics.

    This endpoint returns the current Premier League table with comprehensive team statistics.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        header (str, optional): Include additional metadata in response if provided

    Returns:
        tuple: JSON response containing:
            - dict: League standings with detailed team statistics
            - int: HTTP status code
    """
    season = request.args.get("season")
    header = request.args.get("header")
    response = RankingService().get_premier_league_ranking(season=season, header=header)
    return jsonify(response[0]), response[1]


@ranking_bp.route('/ranking/table', methods=['GET'])
def get_standings_table():
    """Get a simplified Premier League standings table.

    This endpoint returns a streamlined version of the league table focused on essential stats.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')

    Returns:
        tuple: JSON response containing:
            - list: Array of team standings with basic statistics
            - int: HTTP status code
    """
    season = request.args.get("season")
    response = RankingService().get_premier_league_ranking_list(season)
    return jsonify(response[0]), response[1]


@ranking_bp.route('/ranking/csv_file', methods=['GET'])
@safe_file_cleanup
def get_standings_csv():
    """Export Premier League standings to a CSV file.

    This endpoint generates and returns a CSV file containing the complete league table.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        filename (str, required): Name for the exported file (without extension)

    Returns:
        file: CSV file download response

    Error Responses:
        400: Missing filename parameter - when filename is not provided
    """
    if not hasattr(g, 'temp_state'):
        g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    if file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = RankingService().get_premier_league_ranking_csv(safe_filename, season)
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'{file_name}.csv'
                         )
    return response


@ranking_bp.route('/ranking/json_file', methods=['GET'])
@safe_file_cleanup
def get_standings_json():
    """Export Premier League standings to a JSON file.

    This endpoint generates and returns a JSON file containing the complete league table.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        filename (str, required): Name for the exported file (without extension)

    Returns:
        file: JSON file download response

    Error Responses:
        400: Missing filename parameter - when filename is not provided
    """
    if not hasattr(g, 'temp_state'):
        g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    if file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = RankingService().get_premier_league_ranking_json(safe_filename, season)
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='application/json',
                         as_attachment=True,
                         download_name=f'{file_name}.json'
                         )
    return response


@ranking_bp.route('/ranking/pdf_file', methods=['GET'])
@safe_file_cleanup
def get_standings_pdf():
    """Export Premier League standings to a PDF file.

    This endpoint generates and returns a PDF file containing the complete league table
    in a formatted, printable layout.

    Query Parameters:
        season (str, optional): Filter results by season (e.g., '2023-2024')
        filename (str, required): Name for the exported file (without extension)

    Returns:
        file: PDF file download response

    Error Responses:
        400: Missing filename parameter - when filename is not provided
    """
    if not hasattr(g, 'temp_state'):
        g.temp_state = {}
    season = request.args.get("season")
    file_name = request.args.get("filename")
    if file_name is None:
        return {"error": "Missing filename parameter"}, 400

    # Secure the filename to prevent directory traversal attacks
    safe_filename = secure_filename(file_name)
    response = RankingService().get_premier_league_ranking_pdf(safe_filename, season)
    g.temp_state['file_path'] = response[0]

    if response[1] == 200:
        file_path = response[0]
        return send_file(file_path,
                         mimetype='application/pdf',
                         as_attachment=True,
                         download_name=f'{file_name}.pdf'
                         )
    return response