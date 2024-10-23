from flask import Flask
from config import Config
from .routes.ranking import ranking_bp
from .routes.players import players_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.sort_keys = False
    app.register_blueprint(players_bp)
    # app.register_blueprint(transfers_bp)
    app.register_blueprint(ranking_bp)

    return app
