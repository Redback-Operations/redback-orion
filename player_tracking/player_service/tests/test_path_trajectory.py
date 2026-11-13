import asyncio
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import UploadFile


SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))

import config
from routes.path_trajectory import path_trajectory


class PathTrajectoryRouteTests(unittest.TestCase):
    def test_response_exposes_metrics_metadata_and_hides_internal_csv_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            uploads_dir = temp_path / "uploads"
            outputs_dir = temp_path / "outputs"

            uploads_dir.mkdir()
            outputs_dir.mkdir()

            fake_upload = UploadFile(
                filename="sample.mp4",
                file=io.BytesIO(b"fake video"),
            )

            fake_result = {
                "video_path": "internal/input.mp4",
                "model_path": "internal/model.pt",
                "output_video_path": "internal/output.mp4",
                "output_json_path": "internal/output.json",
                "output_csv_path": "internal/player_metrics.csv",
                "fps": 25.0,
                "processed_frames": 100,
                "movement_metrics": {
                    "metric_mode": "pixel_estimate",
                    "calibration_available": False,
                    "exported_tracks": 3,
                    "metrics_csv_path": "internal/player_metrics.csv",
                },
                "tracks": [],
            }

            captured_config = {}

            def fake_process_video(tracking_config):
                captured_config["config"] = tracking_config
                return fake_result

            class FakeTrackingConfig:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)

            fake_config_module = type(sys)("player_tracking.config")
            fake_config_module.TrackingConfig = FakeTrackingConfig

            fake_processor_module = type(sys)("player_tracking.video_processor")
            fake_processor_module.process_video = fake_process_video

            with (
                patch.object(config, "UPLOADS_DIR", uploads_dir),
                patch.object(config, "OUTPUTS_DIR", outputs_dir),
                patch.dict(
                    sys.modules,
                    {
                        "player_tracking.config": fake_config_module,
                        "player_tracking.video_processor": fake_processor_module,
                    },
                ),
            ):
                response = asyncio.run(
                    path_trajectory(fake_upload)
                )

            tracking_config = captured_config["config"]

            self.assertEqual(
                tracking_config.output_csv_path.parent,
                outputs_dir,
            )

            self.assertTrue(
                tracking_config.output_csv_path.name.endswith(
                    "_player_metrics.csv"
                )
            )

            self.assertEqual(
                response["status"],
                "success",
            )

            self.assertEqual(
                response["metric_mode"],
                "pixel_estimate",
            )

            self.assertFalse(
                response["calibration_available"]
            )

            self.assertTrue(
                response["metrics_csv_url"].startswith(
                    "/outputs/"
                )
            )

            self.assertTrue(
                response["metrics_csv_url"].endswith(
                    "_player_metrics.csv"
                )
            )

            self.assertNotIn(
                "output_csv_path",
                response,
            )

            self.assertNotIn(
                "video_path",
                response,
            )

            self.assertNotIn(
                "model_path",
                response,
            )

            self.assertNotIn(
                "output_video_path",
                response,
            )

            self.assertNotIn(
                "output_json_path",
                response,
            )


if __name__ == "__main__":
    unittest.main()