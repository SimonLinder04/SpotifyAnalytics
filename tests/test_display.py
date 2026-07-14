import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from spotify_analytics.display import LIST_SEPARATOR, display_data, item_summary


class DisplayTests(unittest.TestCase):
    def test_summarizes_non_dictionary_item(self):
        self.assertEqual(item_summary("Example"), "Example")

    def test_simple_list_has_numbering_and_separators(self):
        output = StringIO()
        with (
            patch(
                "spotify_analytics.display.load_settings",
                return_value={"view_mode": "simple", "item_limit": 10},
            ),
            redirect_stdout(output),
        ):
            display_data({"items": [{"name": "One"}, {"name": "Two"}]})

        self.assertEqual(
            output.getvalue().splitlines(),
            [LIST_SEPARATOR, "1. One", "2. Two", LIST_SEPARATOR],
        )

    def test_single_resource_has_no_separators(self):
        output = StringIO()
        with (
            patch(
                "spotify_analytics.display.load_settings",
                return_value={"view_mode": "simple", "item_limit": 10},
            ),
            redirect_stdout(output),
        ):
            display_data({"name": "One"})

        self.assertNotIn(LIST_SEPARATOR, output.getvalue())


if __name__ == "__main__":
    unittest.main()
