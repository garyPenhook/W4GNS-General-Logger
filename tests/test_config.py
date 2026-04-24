import json
import os
import tempfile
import unittest

from src.config import Config


class ConfigPersistenceTests(unittest.TestCase):
    def test_rapid_consecutive_sets_are_written_to_disk(self):
        with tempfile.TemporaryDirectory() as tempdir:
            config_path = os.path.join(tempdir, "config.json")
            config = Config(config_path=config_path)

            config.set("first", "saved")
            config.set("second", "also_saved")

            with open(config_path, encoding="utf-8") as handle:
                data = json.load(handle)

            self.assertEqual(data["first"], "saved")
            self.assertEqual(data["second"], "also_saved")


if __name__ == "__main__":
    unittest.main()
