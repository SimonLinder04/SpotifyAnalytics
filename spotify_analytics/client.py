from urllib.parse import urlparse

import requests

from spotify_analytics.auth import get_access_token
from spotify_analytics.config import API_BASE_URL


def extract_spotify_id(value, resource_type):
    value = value.strip()
    uri_prefix = f"spotify:{resource_type}:"
    if value.startswith(uri_prefix):
        return value.removeprefix(uri_prefix).split("?", 1)[0]

    parsed_url = urlparse(value)
    if parsed_url.netloc.lower() not in {"open.spotify.com", "play.spotify.com"}:
        return None

    path_parts = [part for part in parsed_url.path.split("/") if part]
    for index, part in enumerate(path_parts[:-1]):
        if part == resource_type:
            return path_parts[index + 1]
    return None


def spotify_get(path, parameters=None):
    api_prefix = f"{API_BASE_URL}/"
    url = path if path.startswith(api_prefix) else f"{api_prefix}{path.lstrip('/')}"
    response = requests.get(
        url,
        params=parameters,
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Accept": "application/json",
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def spotify_get_items(path, item_count, parameters=None):
    request_parameters = dict(parameters or {})
    request_parameters["limit"] = min(item_count, 50)
    page = spotify_get(path, request_parameters)
    combined_page = dict(page)
    combined_items = list(page.get("items", []))

    next_page = page.get("next")
    while next_page and len(combined_items) < item_count:
        page = spotify_get(next_page)
        combined_items.extend(page.get("items", []))
        next_page = page.get("next")

    combined_page["items"] = combined_items[:item_count]
    combined_page["limit"] = item_count
    combined_page["next"] = next_page
    return combined_page
