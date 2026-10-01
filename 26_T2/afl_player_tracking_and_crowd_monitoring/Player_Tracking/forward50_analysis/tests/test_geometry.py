import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry import assign_zone, contains, ground_point, scale_polygon


class GeometryTests(unittest.TestCase):
    def test_ground_point_uses_bottom_centre(self):
        self.assertEqual(ground_point((10, 20, 30, 80)), (20.0, 80.0))

    def test_invalid_bbox_is_rejected(self):
        with self.assertRaises(ValueError):
            ground_point((30, 20, 10, 80))

    def test_normalized_polygon_is_scaled(self):
        polygon = scale_polygon([[0, 0], [1, 0], [1, 1]], 100, 50)
        np.testing.assert_array_equal(polygon, [[0, 0], [100, 0], [100, 50]])

    def test_boundary_point_counts_as_inside(self):
        polygon = np.array([[0, 0], [100, 0], [100, 100], [0, 100]], dtype=np.int32)
        self.assertTrue(contains((0, 50), polygon))
        self.assertFalse(contains((101, 50), polygon))

    def test_zone_assignment(self):
        zones = {
            "left": np.array([[0, 0], [50, 0], [50, 100], [0, 100]], dtype=np.int32),
            "right": np.array([[51, 0], [100, 0], [100, 100], [51, 100]], dtype=np.int32),
        }
        self.assertEqual(assign_zone((25, 40), zones), "left")
        self.assertEqual(assign_zone((75, 40), zones), "right")
        self.assertIsNone(assign_zone((150, 40), zones))


if __name__ == "__main__":
    unittest.main()

