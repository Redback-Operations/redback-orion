import csv
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from player_tracking.config import TrackingConfig
from player_tracking.metrics import export_player_metrics_csv


class MetricsCalibrationTests(unittest.TestCase):
    def make_track(self):
        return SimpleNamespace(
            track_id=1,
            cluster_id=None,
            cluster_team="Unknown",
            initial_class_id=0,
            initial_class_name="PLAYER",
            jersey_features=[],
            frames=[
                {
                    "frame_index": 0,
                    "time_sec": 0.0,
                    "center": [0.0, 0.0],
                    "ground_point": [0.0, 0.0],
                },
                {
                    "frame_index": 1,
                    "time_sec": 1.0,
                    "center": [100.0, 0.0],
                    "ground_point": [100.0, 0.0],
                },
            ],
        )

    def read_single_row(self, path):
        with open(path, newline="", encoding="utf-8") as f:
            return next(csv.DictReader(f))

    def test_fallback_uses_pixel_to_meter(self):
        config = TrackingConfig(
            pixel_to_meter=0.05,
            max_speed_kmh=1000.0,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "metrics.csv"

            summary = export_player_metrics_csv(
                tracks={1: self.make_track()},
                csv_path=output_path,
                fps=30.0,
                config=config,
            )

            row = self.read_single_row(output_path)

        self.assertAlmostEqual(
            float(row["total_distance_px"]),
            100.0,
            places=3,
        )
        self.assertAlmostEqual(
            float(row["total_distance_m"]),
            5.0,
            places=3,
        )
        self.assertAlmostEqual(
            float(row["avg_speed_kmh"]),
            18.0,
            places=3,
        )

        self.assertEqual(
            row["metric_mode"],
            "pixel_estimate",
        )
        self.assertEqual(
            row["calibration_available"],
            "False",
        )

        self.assertEqual(
            summary["metric_mode"],
            "pixel_estimate",
        )
        self.assertFalse(
            summary["calibration_available"]
        )
        self.assertEqual(
            summary["exported_tracks"],
            1,
        )
        self.assertEqual(
            summary["metrics_csv_path"],
            str(output_path),
        )

    def test_calibration_uses_field_coordinates(self):
        config = TrackingConfig(
            pixel_to_meter=0.05,
            max_speed_kmh=1000.0,
            image_calibration_points=[
                (0.0, 0.0),
                (100.0, 0.0),
                (100.0, 100.0),
                (0.0, 100.0),
            ],
            field_calibration_points=[
                (0.0, 0.0),
                (50.0, 0.0),
                (50.0, 50.0),
                (0.0, 50.0),
            ],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "metrics.csv"

            summary = export_player_metrics_csv(
                tracks={1: self.make_track()},
                csv_path=output_path,
                fps=30.0,
                config=config,
            )

            row = self.read_single_row(output_path)

        self.assertAlmostEqual(
            float(row["total_distance_px"]),
            100.0,
            places=3,
        )
        self.assertAlmostEqual(
            float(row["total_distance_m"]),
            50.0,
            places=3,
        )
        self.assertAlmostEqual(
            float(row["avg_speed_kmh"]),
            180.0,
            places=3,
        )

        self.assertEqual(
            row["metric_mode"],
            "field_calibrated",
        )
        self.assertEqual(
            row["calibration_available"],
            "True",
        )

        self.assertEqual(
            summary["metric_mode"],
            "field_calibrated",
        )
        self.assertTrue(
            summary["calibration_available"]
        )
        self.assertEqual(
            summary["exported_tracks"],
            1,
        )
        self.assertEqual(
            summary["metrics_csv_path"],
            str(output_path),
        )


if __name__ == "__main__":
    unittest.main()