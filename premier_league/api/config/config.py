import os
from dataclasses import dataclass, field
from typing import Any, Dict

import yaml


@dataclass
class ServerConfig:
    """Server configuration settings."""

    HOST: str = "0.0.0.0"
    PORT: int = 3000
    DEBUG: bool = False
    SECRET_KEY: str = "default-secret-key"
    CORS_ORIGINS: list = field(default_factory=lambda: ["*"])
    JSON_SORT_KEYS: bool = False
    RATE_LIMIT: int = 100
    CACHE_TYPE: str = "simple"
    CACHE_DEFAULT_TIMEOUT: int = 300
    LOG_LEVEL: str = "INFO"

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ServerConfig":
        """Create config from dictionary."""
        return cls(
            **{
                k: v
                for k, v in config_dict.items()
                if k in ServerConfig.__annotations__
            }
        )

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ServerConfig":
        """Load config from YAML file."""
        with open(yaml_path, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Load config from environment variables."""
        config_dict = {}
        for key in cls.__annotations__:
            env_val = os.getenv(f"PREMIER_LEAGUE_{key}")
            if env_val is not None:
                if key in ["PORT", "RATE_LIMIT", "CACHE_DEFAULT_TIMEOUT"]:
                    config_dict[key] = int(env_val)
                elif key in ["DEBUG"]:
                    config_dict[key] = env_val.lower() == "true"
                elif key in ["CORS_ORIGINS"]:
                    config_dict[key] = env_val.split(",")
                else:
                    config_dict[key] = env_val
        return cls.from_dict(config_dict)
