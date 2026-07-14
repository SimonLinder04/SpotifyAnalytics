import json
from typing import Any


RESOURCE_EXAMPLES: dict[str, Any] = {
    "artist": {
        "id": "artist_id",
        "name": "Example Artist",
        "type": "artist",
        "genres": ["example genre"],
        "followers": {"total": 12345},
        "external_urls": {
            "spotify": "https://open.spotify.com/artist/artist_id",
        },
    },
    "track": {
        "id": "track_id",
        "name": "Example Track",
        "type": "track",
        "duration_ms": 210000,
        "explicit": False,
        "artists": [{"id": "artist_id", "name": "Example Artist"}],
        "album": {"id": "album_id", "name": "Example Album"},
        "external_urls": {
            "spotify": "https://open.spotify.com/track/track_id",
        },
    },
    "album": {
        "id": "album_id",
        "name": "Example Album",
        "type": "album",
        "album_type": "album",
        "total_tracks": 10,
        "release_date": "2026-01-01",
        "artists": [{"id": "artist_id", "name": "Example Artist"}],
        "tracks": {
            "items": [{"id": "track_id", "name": "Example Track"}],
        },
        "external_urls": {
            "spotify": "https://open.spotify.com/album/album_id",
        },
    },
    "playlist": {
        "id": "playlist_id",
        "name": "Example Playlist",
        "type": "playlist",
        "description": "An example playlist",
        "owner": {"id": "owner_id", "display_name": "Example User"},
        "public": True,
        "items": {"total": 25},
        "external_urls": {
            "spotify": "https://open.spotify.com/playlist/playlist_id",
        },
    },
    "playlist_items": {
        "items": [
            {
                "added_at": "2026-01-01T12:00:00Z",
                "item": {
                    "id": "track_id",
                    "name": "Example Track",
                    "type": "track",
                    "artists": [{"id": "artist_id", "name": "Example Artist"}],
                    "album": {"id": "album_id", "name": "Example Album"},
                },
            }
        ],
        "total": 1,
    },
}

EXAMPLE_LINKS = {
    "artist": "https://open.spotify.com/artist/60d24wfXkVzDSfLS6hyCjZ",
    "track": "https://open.spotify.com/track/7KPr0YxECy4Q1k2F17Sa0Q",
    "album": "https://open.spotify.com/album/45gsxfnJ5Nt2RZp82SQenc",
    "playlist": "https://open.spotify.com/playlist/48rEc61Pe7Re07vlo3gvZ7",
    "playlist_items": "https://open.spotify.com/playlist/48rEc61Pe7Re07vlo3gvZ7",
}


def example_json(example_name: str) -> str:
    try:
        example = RESOURCE_EXAMPLES[example_name]
    except KeyError as error:
        raise ValueError(f"Unknown example: {example_name}") from error
    return json.dumps(example, indent=2, ensure_ascii=False)
