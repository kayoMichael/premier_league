import logging
from typing import Optional, Union

import gunicorn.app.base
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from premier_league.api.config.config import ServerConfig
from premier_league.api.routes.players import players_bp
from premier_league.api.routes.ranking import ranking_bp
from premier_league.api.routes.transfer import transfer_bp


class StandaloneGunicornApp(gunicorn.app.base.BaseApplication):
    """Standalone Gunicorn application for running the Flask app in production mode."""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self):
        return self.application


def create_app(config: Optional[Union[ServerConfig, str, dict]] = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = ServerConfig.from_env()
    elif isinstance(config, str):
        config = ServerConfig.from_yaml(config)
    elif isinstance(config, dict):
        config = ServerConfig.from_dict(config)

    # Apply configuration from settings
    app.config.update(
        {
            "SERVER_NAME": (
                f"{config.HOST}:{config.PORT}" if config.HOST != "0.0.0.0" else None
            ),
            "DEBUG": config.DEBUG,
            "SECRET_KEY": config.SECRET_KEY,
            "JSON_SORT_KEYS": config.JSON_SORT_KEYS,
            "CACHE_TYPE": config.CACHE_TYPE,
            "CACHE_DEFAULT_TIMEOUT": config.CACHE_DEFAULT_TIMEOUT,
        }
    )

    logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))

    CORS(app, origins=config.CORS_ORIGINS)
    Cache(app)
    Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[f"{config.RATE_LIMIT} per minute"],
    )

    app.register_blueprint(players_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(ranking_bp)

    return app, config


def run_server(
    host: str = "0.0.0.0",
    port: int = 3000,
    debug: bool = False,
    config_path: Optional[str] = None,
    config_dict: Optional[dict] = None,
    mode: str = "development",
    workers: int = 1,
) -> None:
    """
    Run the Premier League API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
        config_path: Path to YAML config file
        config_dict: Dictionary of configuration options
        mode: Run mode (development or production)
        workers: Number of Gunicorn workers

    Example:
        >>> from premier_league import run_server
        >>> run_server(port=8000, debug=True)
    """
    if config_path:
        config = ServerConfig.from_yaml(config_path)
    elif config_dict:
        config = ServerConfig.from_dict(config_dict)
    else:
        config = ServerConfig(HOST=host, PORT=port, DEBUG=debug)

    app, config = create_app(config)
    if mode == "development":
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    else:
        options = {
            "bind": f"{config.HOST}:{config.PORT}",
            "workers": workers,
            "worker_class": "sync",
            "timeout": 120,
            "preload_app": True,
        }
        StandaloneGunicornApp(app, options).run()
