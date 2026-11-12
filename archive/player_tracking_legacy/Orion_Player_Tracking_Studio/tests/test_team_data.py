import csv
import tempfile
import threading
import unittest
from pathlib import Path

from review_tool.core import ReviewProject, TrackRow, summarise_tracks
from review_tool.camera import analyze_camera


class TeamDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.project = ReviewProject(rows=[TrackRow(0, "7", "PLAYER", .9), TrackRow(1, "7", "PLAYER", .8)])
        self.project.tracks = summarise_tracks(self.project.rows)
        self.project.resolve_identities()

    def source(self, rows):
        path = self.folder / "movement.csv"
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["frame", "player_id", "speed_kmh", "zone"])
            writer.writerows(rows)
        return path

    def test_import_export_restore_and_corrections(self):
        self.project.import_team_data(self.source([[1, 7, 12, "A"], [2, 7, 15, "B"]]), -1)
        self.project.set_track_value("7", "team", "Team 1")
        self.project.set_track_value("7", "jumper", "9")
        self.project.camera_analysis = {"records": [], "processed_frames": 2}
        paths = self.project.export(self.folder / "export")
        restored = ReviewProject.restore(paths["project"])
        self.assertEqual(restored.rows[1].extras["zone"], "B")
        self.assertEqual(restored.team_data_sources[0]["frame_offset"], -1)
        self.assertEqual(restored.camera_analysis, self.project.camera_analysis)
        with paths["detections"].open() as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[1]["imported_speed_kmh"], "15")
        self.assertEqual(rows[1]["stable_id"], "Team 1 9")

    def test_invalid_import_is_atomic(self):
        for data in ([[0, 7, 12, "A"], [2, 7, 15, "B"]], [[0, 7, 12, "A"], [0, 7, 15, "B"]]):
            with self.assertRaises(ValueError):
                self.project.import_team_data(self.source(data))
            self.assertFalse(self.project.rows[0].extras)
            self.assertFalse(self.project.team_data_sources)

    def test_extra_columns_preserved_on_tracking_load(self):
        self.project.load_csv(self.source([[0, 7, 12, "A"]]))
        self.assertEqual(self.project.rows[0].extras, {"speed_kmh": "12", "zone": "A"})

    def test_camera_translation_and_stop(self):
        import cv2
        import numpy as np
        path = self.folder / "camera.avi"
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (240, 180))
        self.assertTrue(writer.isOpened())
        rng = np.random.default_rng(7)
        base = rng.integers(0, 256, (180, 240, 3), dtype=np.uint8)
        for index in range(10):
            writer.write(cv2.warpAffine(base, np.float32([[1, 0, index * 2], [0, 1, 0]]), (240, 180)))
        writer.release()
        result = analyze_camera(path, 10)
        self.assertEqual(result["processed_frames"], 10)
        self.assertGreater(len(result["records"]), 5)
        self.assertAlmostEqual(result["mean"], 2, delta=.4)
        stop = threading.Event()
        result = analyze_camera(path, 10, stop, lambda *args: stop.set())
        self.assertTrue(result["stopped"])
        self.assertEqual(result["processed_frames"], 2)
        with self.assertRaises(ValueError):
            analyze_camera(path, 1)


if __name__ == "__main__":
    unittest.main()
