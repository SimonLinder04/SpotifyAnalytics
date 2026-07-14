import json
from collections.abc import Callable

import requests

from spotify_analytics.auth import sign_in
from spotify_analytics.client import extract_spotify_id, spotify_get, spotify_get_items
from spotify_analytics.config import load_environment_file
from spotify_analytics.display import display_data
from spotify_analytics.examples import EXAMPLE_LINKS, example_json
from spotify_analytics.settings import (
    MIN_ITEM_LIMIT,
    load_settings,
    save_item_limit,
    save_view_mode,
)


MAIN_MENU_OPTIONS = (
    "1. Get artist info from artist link",
    "2. Get song info from song link",
    "3. Get album info from album link",
    "4. Get playlist info from playlist link",
    "5. Get playlist items from playlist link",
    "6. Get my playlists",
    "7. Get my top tracks",
    "8. Get my top artists",
    "9. Get my recently played tracks",
    "10. Sign in or reconnect Spotify account",
    "11. Settings",
    "0. Exit",
)
MENU_SEPARATOR = "-" * 60


def print_menu(title: str, options: tuple[str, ...]) -> None:
    print(f"\n{MENU_SEPARATOR}")
    print(title)
    for option in options:
        print(option)
    print(MENU_SEPARATOR)


def display_items(items: list[object]) -> None:
    display_data({"items": items})


def choose_link_or_example() -> str:
    print_menu(
        "Resource options",
        (
            "1. Enter a Spotify link",
            "2. Show example JSON",
            "0. Back",
        ),
    )
    choice = input("Choose an option: ").strip()
    if choice == "1":
        return "link"
    if choice == "2":
        return "example"
    if choice != "0":
        print("Invalid option. Choose a number from 0 to 2.")
    return "back"


def print_example_blueprint(example_name: str) -> None:
    print("\nExample blueprint:")
    print(example_json(example_name))


def print_live_json(data: object) -> None:
    print("\nLive Spotify response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def get_linked_resource(resource_type: str) -> None:
    choice = choose_link_or_example()
    if choice == "back":
        return

    if choice == "example":
        print_example_blueprint(resource_type)
        spotify_link = EXAMPLE_LINKS[resource_type]
    else:
        spotify_link = input(f"Enter the Spotify {resource_type} link: ").strip()

    resource_id = extract_spotify_id(spotify_link, resource_type)
    if not resource_id:
        print(f"That is not a valid Spotify {resource_type} link or URI.")
        return
    data = spotify_get(f"{resource_type}s/{resource_id}")
    if choice == "example":
        print_live_json(data)
    else:
        display_data(data)


def get_playlist_items() -> None:
    choice = choose_link_or_example()
    if choice == "back":
        return

    if choice == "example":
        print_example_blueprint("playlist_items")
        spotify_link = EXAMPLE_LINKS["playlist_items"]
    else:
        spotify_link = input("Enter the Spotify playlist link: ").strip()

    playlist_id = extract_spotify_id(spotify_link, "playlist")
    if not playlist_id:
        print("That is not a valid Spotify playlist link or URI.")
        return
    settings = load_settings()
    items = spotify_get_items(
        f"playlists/{playlist_id}/items",
        settings["item_limit"],
    )
    if choice == "example":
        print_live_json({"items": items})
    else:
        display_items(items)


def get_my_playlists() -> None:
    settings = load_settings()
    display_items(
        spotify_get_items(
            "me/playlists",
            settings["item_limit"],
        )
    )


def get_my_top(item_type: str) -> None:
    time_ranges = {
        "1": "short_term",
        "2": "medium_term",
        "3": "long_term",
    }
    print_menu(
        "Time range",
        (
            "1. Last 1 month",
            "2. Last 6 months",
            "3. Last 12 months",
        ),
    )
    selected_range = input("Choose a time range [2]: ").strip() or "2"
    time_range = time_ranges.get(selected_range)
    if not time_range:
        print("Invalid time range.")
        return

    settings = load_settings()
    items = spotify_get_items(
        f"me/top/{item_type}",
        settings["item_limit"],
        {
            "time_range": time_range,
        },
    )
    display_items(items)


def get_recently_played() -> None:
    item_limit = load_settings()["item_limit"]
    display_items(spotify_get_items("me/player/recently-played", item_limit))


def change_view_mode() -> None:
    settings = load_settings()
    print_menu(
        f"Display mode (current: {settings['view_mode']})",
        (
            "1. Simple view",
            "2. JSON view",
            "3. Padded view",
        ),
    )

    choices = {"1": "simple", "2": "json", "3": "padded"}
    choice = input("Choose a display mode: ").strip()
    view_mode = choices.get(choice)
    if not view_mode:
        print("Invalid display mode.")
        return

    save_view_mode(view_mode)
    print(f"View mode changed to {view_mode}.")


def change_item_limit() -> None:
    settings = load_settings()
    print(f"Items currently displayed: {settings['item_limit']}")
    value = input(f"Number of items (minimum {MIN_ITEM_LIMIT}): ").strip()
    try:
        item_limit = int(value)
        save_item_limit(item_limit)
    except ValueError:
        print(f"Enter a whole number of at least {MIN_ITEM_LIMIT}.")
        return

    print(f"Items displayed changed to {item_limit}.")


def open_settings() -> None:
    print_menu(
        "Settings",
        (
            "1. Change display mode",
            "2. Change number of items displayed",
            "0. Back",
        ),
    )

    actions: dict[str, Callable[[], None]] = {
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


def show_http_error(error: requests.HTTPError) -> None:
    response = error.response
    status_code = response.status_code if response is not None else "unknown"
    message = response.reason if response is not None else str(error)
    try:
        response_data = response.json()
        api_error = response_data.get("error")
        if isinstance(api_error, dict):
            message = api_error.get("message", message)
        elif isinstance(api_error, str):
            message = response_data.get("error_description", api_error)
    except (AttributeError, requests.exceptions.JSONDecodeError):
        pass

    print(f"Spotify returned HTTP {status_code}: {message}")
    if status_code == 401:
        print("Use option 10 to sign in again.")
    elif status_code == 403:
        print("The signed-in account did not grant the permission required by this option.")


def print_main_menu() -> None:
    print_menu("Spotify Analytics", MAIN_MENU_OPTIONS)


def main() -> None:
    load_environment_file()
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: get_linked_resource("artist"),
        "2": lambda: get_linked_resource("track"),
        "3": lambda: get_linked_resource("album"),
        "4": lambda: get_linked_resource("playlist"),
        "5": get_playlist_items,
        "6": get_my_playlists,
        "7": lambda: get_my_top("tracks"),
        "8": lambda: get_my_top("artists"),
        "9": get_recently_played,
        "10": sign_in,
        "11": open_settings,
    }

    while True:
        print_main_menu()

        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye.")
            return

        action = actions.get(choice)
        if not action:
            print("Invalid option. Choose a number from 0 to 11.")
            continue

        try:
            action()
        except requests.HTTPError as error:
            show_http_error(error)
        except requests.RequestException as error:
            print(f"Could not reach Spotify: {error}")
        except RuntimeError as error:
            print(error)
