import json
from typing import TypedDict

from spotify_analytics.config import PROJECT_DIRECTORY


SETTINGS_FILE = PROJECT_DIRECTORY / "settings.json"


class Settings(TypedDict):
    view_mode: str
    item_limit: int


DEFAULT_SETTINGS: Settings = {"view_mode": "padded", "item_limit": 10}
VIEW_MODES = ("simple", "json", "padded")
MIN_ITEM_LIMIT = 1


def load_settings() -> Settings:
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

    validated_settings = DEFAULT_SETTINGS.copy()
    if settings.get("view_mode") in VIEW_MODES:
        validated_settings["view_mode"] = settings["view_mode"]

    item_limit = settings.get("item_limit")
    if isinstance(item_limit, int) and not isinstance(item_limit, bool):
        if item_limit >= MIN_ITEM_LIMIT:
            validated_settings["item_limit"] = item_limit

    return validated_settings


def save_settings(settings: Settings) -> None:
    SETTINGS_FILE.write_text(json.dumps(settings, indent=4) + "\n", encoding="utf-8")


def save_view_mode(view_mode: str) -> None:
    if view_mode not in VIEW_MODES:
        raise ValueError(f"Unknown view mode: {view_mode}")

    settings = load_settings()
    settings["view_mode"] = view_mode
    save_settings(settings)


def save_item_limit(item_limit: int) -> None:
    if (
        not isinstance(item_limit, int)
        or isinstance(item_limit, bool)
        or item_limit < MIN_ITEM_LIMIT
    ):
        raise ValueError(f"Item limit must be at least {MIN_ITEM_LIMIT}.")

    settings = load_settings()
    settings["item_limit"] = item_limit
    save_settings(settings)
