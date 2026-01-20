import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# -----------------------------
# Environment selector
# -----------------------------
class EnvSettings(BaseSettings):
    """Select the environment (dev/prod/etc). Defaults to 'dev'."""

    env: str = "dev"

    model_config = SettingsConfigDict(
        env_file=None,  # No static env file
        env_file_encoding="utf-8",
        extra="ignore",
    )


# -----------------------------
# API / App settings
# -----------------------------
class ApiSettings(BaseSettings):
    todo_client_domain: str
    demo_config: bool
    demo_database_url: str

    model_config = SettingsConfigDict(
        env_file=None,  # Will be set at runtime
        env_file_encoding="utf-8",
        extra="ignore",
    )


# -----------------------------
# Cached getters
# -----------------------------
@lru_cache()
def get_env_setting() -> EnvSettings:
    """
    Load the base environment settings.
    Uses system ENV variable if set; otherwise defaults to 'dev'.
    """
    env_from_system = os.getenv("ENV")
    return EnvSettings(env=env_from_system) if env_from_system else EnvSettings()


@lru_cache()
def get_api_settings() -> ApiSettings:
    """
    Load API settings from environment-specific .env file.
    Falls back to dev.env if the specific environment file is missing.
    """
    env_setting = get_env_setting()
    env_name = env_setting.env

    base_dir = Path(__file__).resolve().parent.parent  # project root
    env_file_path = os.path.join(base_dir, "environments", f"{env_name}.env")
    # env_file_path = base_dir / "environments" / f"{env_name}.env"

    # Fallback to dev.env if the specific environment file does not exist
    if not os.path.exists(env_file_path):
        fallback_path = os.path.join(base_dir, "environments", "dev.env")
        if os.path.exists(fallback_path):
            env_file_path = fallback_path
        else:
            raise FileNotFoundError(
                f"No environment file found for '{env_name}' and no dev.env fallback. '{fallback_path}'"
            )

    # Instantiate ApiSettings dynamically from the chosen .env
    return ApiSettings(_env_file=env_file_path)  # type: ignore


# -----------------------------
# Load settings
# -----------------------------
env_settings: EnvSettings = get_env_setting()
api_settings: ApiSettings = get_api_settings()
