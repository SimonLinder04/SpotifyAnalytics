import json
import unittest

from spotify_analytics.examples import EXAMPLE_LINKS, RESOURCE_EXAMPLES, example_json


class ExampleTests(unittest.TestCase):
    def test_every_example_is_valid_json(self):
        for example_name in RESOURCE_EXAMPLES:
            with self.subTest(example_name=example_name):
                self.assertEqual(
                    json.loads(example_json(example_name)),
                    RESOURCE_EXAMPLES[example_name],
                )

    def test_rejects_unknown_example(self):
        with self.assertRaises(ValueError):
            example_json("unknown")

    def test_every_example_has_a_spotify_link(self):
        self.assertEqual(set(EXAMPLE_LINKS), set(RESOURCE_EXAMPLES))
        for link in EXAMPLE_LINKS.values():
            self.assertTrue(link.startswith("https://open.spotify.com/"))


if __name__ == "__main__":
    unittest.main()
