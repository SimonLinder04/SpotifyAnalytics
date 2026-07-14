from urllib.parse import urlparse
from typing import Any, Mapping

import requests

from spotify_analytics.auth import get_access_token
from spotify_analytics.config import API_BASE_URL


def extract_spotify_id(value: str, resource_type: str) -> str | None:
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


def spotify_get(
    path: str, parameters: Mapping[str, Any] | None = None
) -> dict[str, Any]:
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
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError("Spotify returned an unexpected response format.")
    return data


def page_items(page: Mapping[str, Any]) -> list[Any]:
    items = page.get("items", [])
    if not isinstance(items, list):
        raise RuntimeError("Spotify returned an invalid items page.")
    return items


def spotify_get_items(
    path: str,
    item_count: int,
    parameters: Mapping[str, Any] | None = None,
) -> list[Any]:
    if item_count < 1:
        raise ValueError("Item count must be at least 1.")

    request_parameters = dict(parameters or {})
    request_parameters["limit"] = min(item_count, 50)
    page = spotify_get(path, request_parameters)
    combined_items = page_items(page).copy()

    next_page = page.get("next")
    visited_pages: set[str] = set()
    while next_page and len(combined_items) < item_count:
        if not isinstance(next_page, str):
            raise RuntimeError("Spotify returned an invalid pagination link.")
        if next_page in visited_pages:
            raise RuntimeError("Spotify pagination returned the same page more than once.")
        visited_pages.add(next_page)
        page = spotify_get(next_page)
        combined_items.extend(page_items(page))
        next_page = page.get("next")

    return combined_items[:item_count]
