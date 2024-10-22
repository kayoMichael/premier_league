from flask import Blueprint, jsonify, request, send_file, g
from app.services.ranking_service import RankingService
from werkzeug.utils import secure_filename
from app.utils.decorator import safe_file_cleanup

ranking_bp = Blueprint('ranking', __name__)

@ranking_bp.route('/ranking', methods=['GET'])
def get_standings():
    season = request.args.get("season")
    header = request.args.get("header")
    response = RankingService().get_premier_league_ranking(season=season, header=header)
    return jsonify(response[0]), response[1]


@ranking_bp.route('/ranking/table', methods=['GET'])
def get_standings_table():
    season = request.args.get("season")
    response = RankingService().get_premier_league_ranking_list(season)
    return jsonify(response[0]), response[1]


@ranking_bp.route('/ranking/csv', methods=['GET'])
@safe_file_cleanup
def get_standings_csv():
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
