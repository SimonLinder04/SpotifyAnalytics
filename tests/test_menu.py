import unittest
from unittest.mock import patch

from spotify_analytics.menu import (
    MENU_SEPARATOR,
    change_item_limit,
    get_linked_resource,
    get_playlist_items,
    open_settings,
    print_menu,
)


class MenuTests(unittest.TestCase):
    @patch("builtins.print")
    def test_menu_has_horizontal_dividers(self, output):
        print_menu("Example", ("1. First", "0. Back"))

        printed_lines = [call.args[0] for call in output.call_args_list]
        self.assertEqual(printed_lines[0], f"\n{MENU_SEPARATOR}")
        self.assertEqual(printed_lines[-1], MENU_SEPARATOR)

    @patch("spotify_analytics.menu.save_item_limit")
    @patch("spotify_analytics.menu.load_settings")
    @patch("builtins.input", return_value="75")
    def test_changes_item_limit(self, _input, load_settings, save_item_limit):
        load_settings.return_value = {"view_mode": "simple", "item_limit": 10}

        change_item_limit()

        save_item_limit.assert_called_once_with(75)

    @patch("spotify_analytics.menu.change_view_mode")
    @patch("builtins.input", return_value="1")
    def test_settings_dispatches_view_action(self, _input, change_view_mode):
        open_settings()

        change_view_mode.assert_called_once_with()

    @patch("spotify_analytics.menu.spotify_get")
    @patch("builtins.input", return_value="2")
    def test_linked_resource_example_calls_spotify(self, _input, spotify_get):
        spotify_get.return_value = {"id": "live_artist", "type": "artist"}
        with patch("builtins.print") as output:
            get_linked_resource("artist")

        spotify_get.assert_called_once_with("artists/60d24wfXkVzDSfLS6hyCjZ")
        printed_text = "\n".join(str(call.args[0]) for call in output.call_args_list)
        self.assertIn("Example blueprint:", printed_text)
        self.assertIn("Live Spotify response:", printed_text)
        self.assertIn('"id": "live_artist"', printed_text)

    @patch("spotify_analytics.menu.spotify_get_items")
    @patch("builtins.input", return_value="2")
    @patch("spotify_analytics.menu.load_settings")
    def test_playlist_items_example_calls_spotify(
        self,
        load_settings,
        _input,
        spotify_get_items,
    ):
        load_settings.return_value = {"view_mode": "simple", "item_limit": 75}
        spotify_get_items.return_value = [{"item": {"name": "Live track"}}]
        with patch("builtins.print") as output:
            get_playlist_items()

        spotify_get_items.assert_called_once_with(
            "playlists/48rEc61Pe7Re07vlo3gvZ7/items",
            75,
        )
        printed_text = "\n".join(str(call.args[0]) for call in output.call_args_list)
        self.assertIn("Example blueprint:", printed_text)
        self.assertIn("Live Spotify response:", printed_text)
        self.assertIn("Live track", printed_text)


if __name__ == "__main__":
    unittest.main()
