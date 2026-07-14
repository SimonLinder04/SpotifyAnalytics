import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import spotify_analytics.settings as settings


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.settings_file = Path(self.temporary_directory.name) / "settings.json"
        self.settings_file_patch = patch.object(
            settings,
            "SETTINGS_FILE",
            self.settings_file,
        )
        self.settings_file_patch.start()

    def tearDown(self):
        self.settings_file_patch.stop()
        self.temporary_directory.cleanup()

    def test_missing_file_returns_defaults(self):
        self.assertEqual(settings.load_settings(), settings.DEFAULT_SETTINGS)

    def test_invalid_values_are_replaced_by_defaults(self):
        self.settings_file.write_text(
            json.dumps({"view_mode": "unknown", "item_limit": 0}),
            encoding="utf-8",
        )

        self.assertEqual(settings.load_settings(), settings.DEFAULT_SETTINGS)

    def test_saves_large_item_limit(self):
        settings.save_item_limit(250)

        self.assertEqual(settings.load_settings()["item_limit"], 250)

    def test_rejects_boolean_item_limit(self):
        with self.assertRaises(ValueError):
            settings.save_item_limit(True)


if __name__ == "__main__":
    unittest.main()
