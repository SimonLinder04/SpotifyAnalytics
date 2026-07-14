import unittest
from unittest.mock import call, patch

from spotify_analytics.client import extract_spotify_id, spotify_get_items


class ExtractSpotifyIdTests(unittest.TestCase):
    def test_extracts_id_from_url(self):
        value = "https://open.spotify.com/playlist/example?si=abc"

        self.assertEqual(extract_spotify_id(value, "playlist"), "example")

    def test_extracts_id_from_uri(self):
        self.assertEqual(
            extract_spotify_id("spotify:track:example", "track"),
            "example",
        )

    def test_rejects_untrusted_host(self):
        value = "https://example.com/playlist/example"

        self.assertIsNone(extract_spotify_id(value, "playlist"))


class SpotifyPaginationTests(unittest.TestCase):
    @patch("spotify_analytics.client.spotify_get")
    def test_combines_pages_and_trims_to_requested_count(self, spotify_get):
        spotify_get.side_effect = [
            {
                "items": list(range(50)),
                "next": "https://api.spotify.com/v1/page-2",
            },
            {
                "items": list(range(50, 100)),
                "next": "https://api.spotify.com/v1/page-3",
            },
        ]

        items = spotify_get_items("me/playlists", 75)

        self.assertEqual(items, list(range(75)))
        self.assertEqual(
            spotify_get.call_args_list,
            [
                call("me/playlists", {"limit": 50}),
                call("https://api.spotify.com/v1/page-2"),
            ],
        )

    @patch("spotify_analytics.client.spotify_get")
    def test_preserves_parameters_on_first_request(self, spotify_get):
        spotify_get.return_value = {"items": [], "next": None}

        spotify_get_items("me/top/tracks", 10, {"time_range": "short_term"})

        spotify_get.assert_called_once_with(
            "me/top/tracks",
            {"time_range": "short_term", "limit": 10},
        )

    def test_rejects_non_positive_item_count(self):
        with self.assertRaises(ValueError):
            spotify_get_items("me/playlists", 0)

    @patch("spotify_analytics.client.spotify_get")
    def test_rejects_repeated_page(self, spotify_get):
        repeated_page = "https://api.spotify.com/v1/repeated"
        spotify_get.side_effect = [
            {"items": [1], "next": repeated_page},
            {"items": [2], "next": repeated_page},
        ]

        with self.assertRaises(RuntimeError):
            spotify_get_items("me/playlists", 3)


if __name__ == "__main__":
    unittest.main()
