import json

from spotify_analytics.config import PROJECT_DIRECTORY


SETTINGS_FILE = PROJECT_DIRECTORY / "settings.json"
DEFAULT_SETTINGS = {"view_mode": "padded", "item_limit": 10}
VIEW_MODES = ("simple", "json", "padded")
MIN_ITEM_LIMIT = 1
MAX_ITEM_LIMIT = 100000


def load_settings():
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
        if MIN_ITEM_LIMIT <= item_limit <= MAX_ITEM_LIMIT:
            validated_settings["item_limit"] = item_limit

    return validated_settings


def save_settings(settings):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=4) + "\n", encoding="utf-8")


def save_view_mode(view_mode):
    if view_mode not in VIEW_MODES:
        raise ValueError(f"Unknown view mode: {view_mode}")

    settings = load_settings()
    settings["view_mode"] = view_mode
    save_settings(settings)


def save_item_limit(item_limit):
    if not MIN_ITEM_LIMIT <= item_limit <= MAX_ITEM_LIMIT:
        raise ValueError(f"Item limit must be between {MIN_ITEM_LIMIT} and {MAX_ITEM_LIMIT}.")

    settings = load_settings()
    settings["item_limit"] = item_limit
    save_settings(settings)


def change_view_mode():
    settings = load_settings()
    print(f"Current view: {settings['view_mode']}")
    print("1. Simple view")
    print("2. JSON view")
    print("3. Padded view")

    choices = {"1": "simple", "2": "json", "3": "padded"}
    choice = input("Choose a display mode: ").strip()
    view_mode = choices.get(choice)
    if not view_mode:
        print("Invalid display mode.")
        return

    save_view_mode(view_mode)
    print(f"View mode changed to {view_mode}.")


def change_item_limit():
    settings = load_settings()
    print(f"Items currently displayed: {settings['item_limit']}")
    value = input(f"Number of items ({MIN_ITEM_LIMIT}-{MAX_ITEM_LIMIT}): ").strip()
    try:
        item_limit = int(value)
        save_item_limit(item_limit)
    except ValueError:
        print(f"Enter a whole number from {MIN_ITEM_LIMIT} to {MAX_ITEM_LIMIT}.")
        return

    print(f"Items displayed changed to {item_limit}.")


def open_settings():
    print("\nSettings")
    print("1. Change display mode")
    print("2. Change number of items displayed")
    print("0. Back")

    actions = {
        "1": change_view_mode,
        "2": change_item_limit,
    }
    choice = input("Choose a setting: ").strip()
    if choice == "0":
        return

    action = actions.get(choice)
    if not action:
        print("Invalid setting. Choose a number from 0 to 2.")
        return

    action()
