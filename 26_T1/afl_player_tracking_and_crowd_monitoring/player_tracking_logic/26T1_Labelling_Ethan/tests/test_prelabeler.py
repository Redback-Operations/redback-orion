import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402
from labelling_pipeline.prelabeler import classify_by_jersey_color  # noqa: E402


class JerseyColourMappingTests(unittest.TestCase):
    @staticmethod
    def classify(bgr_colour, settings=config):
        image = np.full((100, 100, 3), bgr_colour, dtype=np.uint8)
        return classify_by_jersey_color(settings, image, 0, 0, 99, 99)

    @staticmethod
    def fallback_settings():
        settings = SimpleNamespace(**{
            name: getattr(config, name) for name in dir(config) if name.isupper()
        })
        settings.RED_RATIO_THRES = 2.0
        settings.BLACK_RATIO_THRES = 2.0
        settings.REFEREE_YELLOW_RATIO_THRES = 2.0
        return settings

    def test_red_jersey_maps_to_gold_coast(self):
        self.assertEqual(self.classify((0, 0, 255)), config.TEAM_B_ID)
        self.assertEqual(config.CLASS_NAMES[config.TEAM_B_ID], "GCS")

    def test_dark_jersey_maps_to_carlton(self):
        self.assertEqual(self.classify((20, 20, 20)), config.TEAM_A_ID)
        self.assertEqual(config.CLASS_NAMES[config.TEAM_A_ID], "CAR")

    def test_yellow_jersey_still_maps_to_referee(self):
        self.assertEqual(self.classify((0, 255, 255)), config.REFEREE_ID)

    def test_red_hsv_fallback_maps_to_gold_coast(self):
        self.assertEqual(
            self.classify((0, 0, 255), self.fallback_settings()),
            config.TEAM_B_ID,
        )

    def test_dark_hsv_fallback_maps_to_carlton(self):
        self.assertEqual(
            self.classify((50, 20, 10), self.fallback_settings()),
            config.TEAM_A_ID,
        )


if __name__ == "__main__":
    unittest.main()
