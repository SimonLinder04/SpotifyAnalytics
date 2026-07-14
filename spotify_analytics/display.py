import json
from typing import Any

from spotify_analytics.settings import load_settings

LIST_SEPARATOR = "-" * 60


def contains_list(data: Any) -> bool:
    return isinstance(data, list) or (
        isinstance(data, dict) and isinstance(data.get("items"), list)
    )


def print_data(data: Any, depth: int = 0, max_depth: int = 5) -> None:
    indentation = "    " * depth

    if isinstance(data, dict):
        for key, value in data.items():
            print(indentation + str(key))

            if isinstance(value, (dict, list)):
                if depth < max_depth - 1:
                    print_data(value, depth + 1, max_depth)
            else:
                if depth < max_depth - 1:
                    print("    " * (depth + 1) + str(value))

    elif isinstance(data, list):
        for item in data:
            if depth < max_depth:
                print_data(item, depth, max_depth)

    else:
        print(indentation + str(data))

def item_summary(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)

    content = item.get("track") or item.get("item") or item
    if not isinstance(content, dict):
        return str(content)

    name = content.get("name", "Unnamed item")
    artists = content.get("artists", [])
    artist_names = [artist.get("name") for artist in artists if artist.get("name")]
    if artist_names:
        return f"{name} - {', '.join(artist_names)}"

    owner = content.get("owner", {})
    owner_name = owner.get("display_name") or owner.get("id")
    if owner_name:
        return f"{name} - {owner_name}"
    return name


def print_simple(data: Any) -> None:
    if not isinstance(data, dict):
        print(data)
        return

    items = data.get("items")
    if isinstance(items, list):
        offset = data.get("offset", 0)
        for position, item in enumerate(items, start=offset + 1):
            index = item.get("index", position) if isinstance(item, dict) else position
            print(f"{index}. {item_summary(item)}")
        if not items:
            print("No items found.")
        return

    print(item_summary(data))
    artists = data.get("artists", [])
    album = data.get("album", {})
    genres = data.get("genres", [])
    followers = data.get("followers", {}).get("total")
    spotify_url = data.get("external_urls", {}).get("spotify")

    if artists:
        names = [artist.get("name") for artist in artists if artist.get("name")]
        if names:
            print(f"Artists: {', '.join(names)}")
    if album.get("name"):
        print(f"Album: {album['name']}")
    if genres:
        print(f"Genres: {', '.join(genres)}")
    if followers is not None:
        print(f"Followers: {followers:,}")
    if spotify_url:
        print(f"Spotify: {spotify_url}")


def display_data(data: Any) -> None:
    view_mode = load_settings()["view_mode"]
    has_list = contains_list(data)
    if has_list:
        print(LIST_SEPARATOR)

    if view_mode == "simple":
        print_simple(data)
    elif view_mode == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_data(data, max_depth=5)

    if has_list:
        print(LIST_SEPARATOR)
