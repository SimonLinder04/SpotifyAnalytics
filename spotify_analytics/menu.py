import json

import requests

from spotify_analytics.auth import sign_in
from spotify_analytics.client import extract_spotify_id, spotify_get
from spotify_analytics.config import load_environment_file


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def get_linked_resource(resource_type):
    spotify_link = input(f"Enter the Spotify {resource_type} link: ").strip()
    resource_id = extract_spotify_id(spotify_link, resource_type)
    if not resource_id:
        print(f"That is not a valid Spotify {resource_type} link or URI.")
        return
    print_json(spotify_get(f"{resource_type}s/{resource_id}"))


def get_playlist_items():
    spotify_link = input("Enter the Spotify playlist link: ").strip()
    playlist_id = extract_spotify_id(spotify_link, "playlist")
    if not playlist_id:
        print("That is not a valid Spotify playlist link or URI.")
        return
    print_json(spotify_get(f"playlists/{playlist_id}/items", {"limit": 10}))


def get_my_playlists():
    print_json(spotify_get("me/playlists", {"limit": 10}))


def get_my_top(item_type):
    time_ranges = {
        "1": "short_term",
        "2": "medium_term",
        "3": "long_term",
    }
    print("1. Last 4 weeks")
    print("2. Last 6 months")
    print("3. About the last year")
    selected_range = input("Choose a time range [2]: ").strip() or "2"
    time_range = time_ranges.get(selected_range)
    if not time_range:
        print("Invalid time range.")
        return

    print_json(
        spotify_get(
            f"me/top/{item_type}",
            {"time_range": time_range, "limit": 10},
        )
    )


def get_recently_played():
    print_json(spotify_get("me/player/recently-played", {"limit": 10}))


def show_http_error(error):
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


def main():
    load_environment_file()
    actions = {
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
    }

    while True:
        print("\nSpotify Analytics")
        print("1. Get artist info from artist link")
        print("2. Get song info from song link")
        print("3. Get album info from album link")
        print("4. Get playlist info from playlist link")
        print("5. Get playlist items from playlist link")
        print("6. Get my playlists")
        print("7. Get my top tracks")
        print("8. Get my top artists")
        print("9. Get my recently played tracks")
        print("10. Sign in or reconnect Spotify account")
        print("0. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye.")
            return

        action = actions.get(choice)
        if not action:
            print("Invalid option. Choose a number from 0 to 10.")
            continue

        try:
            action()
        except requests.HTTPError as error:
            show_http_error(error)
        except requests.RequestException as error:
            print(f"Could not reach Spotify: {error}")
        except RuntimeError as error:
            print(error)
