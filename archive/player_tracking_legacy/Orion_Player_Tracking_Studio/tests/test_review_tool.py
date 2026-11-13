import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from review_tool.core import ReviewProject, TrackRow, find_review_events, read_tracking_csv


class ReviewToolTests(unittest.TestCase):
    def write_csv(self, folder: Path, rows: list[dict[str, object]]) -> Path:
        path = folder / "tracks.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_reads_common_column_names(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write_csv(Path(folder), [{
                "frame_id": 8, "player_id": 3, "class_name": "PLAYER", "conf": 0.8,
                "x1": 1, "y1": 2, "x2": 3, "y2": 4,
            }])
            rows = read_tracking_csv(path)
            self.assertEqual(rows[0].frame, 8)
            self.assertEqual(rows[0].track_id, "3")

    def test_resolves_non_overlapping_team_and_jumper_tracks(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write_csv(Path(folder), [
                {"frame": 1, "track_id": 1, "class": "PLAYER", "confidence": 0.8},
                {"frame": 2, "track_id": 1, "class": "PLAYER", "confidence": 0.8},
                {"frame": 20, "track_id": 8, "class": "PLAYER", "confidence": 0.9},
                {"frame": 21, "track_id": 8, "class": "PLAYER", "confidence": 0.9},
            ])
            project = ReviewProject()
            project.load_csv(path)
            for track_id in ("1", "8"):
                project.set_track_value(track_id, "team", "North Melbourne")
                project.set_track_value(track_id, "jumper", "12")
            self.assertEqual(project.tracks["1"].stable_id, "North Melbourne 12")
            self.assertEqual(project.tracks["8"].stable_id, "North Melbourne 12")

    def test_does_not_silently_merge_overlapping_tracks(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write_csv(Path(folder), [
                {"frame": 1, "track_id": 1, "class": "PLAYER", "confidence": 0.8},
                {"frame": 2, "track_id": 1, "class": "PLAYER", "confidence": 0.8},
                {"frame": 2, "track_id": 2, "class": "PLAYER", "confidence": 0.9},
                {"frame": 3, "track_id": 2, "class": "PLAYER", "confidence": 0.9},
            ])
            project = ReviewProject()
            project.load_csv(path)
            for track_id in ("1", "2"):
                project.set_track_value(track_id, "team", "St Kilda")
                project.set_track_value(track_id, "jumper", "7")
            self.assertTrue(project.tracks["1"].stable_id.endswith("review"))

    def test_finds_tracking_review_events(self):
        rows = []
        for frame in range(30):
            rows.extend(TrackRow(frame, str(index), "PLAYER", 0.8) for index in range(2 if frame < 15 else 8))
        events = find_review_events(rows, 25)
        self.assertTrue(any(event.kind == "Detection count change" for event in events))

    def test_exports_review_files(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            path = self.write_csv(base, [{"frame": 1, "track_id": 1, "class": "PLAYER", "confidence": 0.8}])
            project = ReviewProject()
            project.load_csv(path)
            paths = project.export(base / "export")
            self.assertTrue(all(path.exists() for path in paths.values()))


if __name__ == "__main__":
    unittest.main()
