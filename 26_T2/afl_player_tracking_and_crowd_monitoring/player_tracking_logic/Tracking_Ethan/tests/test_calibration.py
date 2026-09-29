import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from player_tracking.calibration import compute_homography, transform_point


class CalibrationTests(unittest.TestCase):
    def test_scale_mapping(self):
        homography = compute_homography(
            [(0, 0), (100, 0), (100, 100), (0, 100)],
            [(0, 0), (50, 0), (50, 50), (0, 50)],
        )

        x, y = transform_point((20, 40), homography)

        self.assertAlmostEqual(x, 10.0, places=4)
        self.assertAlmostEqual(y, 20.0, places=4)

    def test_requires_four_point_pairs(self):
        with self.assertRaises(ValueError):
            compute_homography(
                [(0, 0), (100, 0), (0, 100)],
                [(0, 0), (50, 0), (0, 50)],
            )

    def test_point_lists_must_match(self):
        with self.assertRaises(ValueError):
            compute_homography(
                [(0, 0), (100, 0), (100, 100), (0, 100)],
                [(0, 0), (50, 0), (50, 50)],
            )


if __name__ == "__main__":
    unittest.main()