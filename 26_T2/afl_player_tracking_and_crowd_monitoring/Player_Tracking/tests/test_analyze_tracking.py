import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analyze_tracking.py"
SPEC = importlib.util.spec_from_file_location("analyze_tracking", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeTrackingTests(unittest.TestCase):
    def write_csv(self, directory: Path, rows: list[list[object]]) -> Path:
        path = directory / "tracks.csv"
        with path.open("w", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(["frame", "track_id", "class", "confidence", "x1", "y1", "x2", "y2"])
            writer.writerows(rows)
        return path

    def test_filters_classes_and_flags_short_tracks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self.write_csv(Path(temp), [
                [0, 1, "PLAYER", 0.9, 0, 0, 1, 1],
                [1, 1, "PLAYER", 0.8, 0, 0, 1, 1],
                [2, 1, "PLAYER", 0.7, 0, 0, 1, 1],
                [2, 2, "PLAYER", 0.2, 0, 0, 1, 1],
                [2, 8, "REF", 0.9, 0, 0, 1, 1],
            ])
            report = MODULE.analyze_csv(
                path, fps=2, class_name="player", short_track_seconds=1,
                low_confidence=0.25, count_jump=2, worst_limit=5,
            )
            self.assertEqual(report["summary"]["detections"], 4)
            self.assertEqual(report["summary"]["unique_tracks"], 2)
            self.assertEqual(report["summary"]["short_lived_tracks"], 1)
            self.assertEqual(report["classes"], {"PLAYER": 4})

    def test_detects_large_count_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            rows = [[0, 1, "PLAYER", 0.9, 0, 0, 1, 1]]
            rows.extend([1, track_id, "PLAYER", 0.9, 0, 0, 1, 1] for track_id in range(1, 5))
            path = self.write_csv(Path(temp), rows)
            report = MODULE.analyze_csv(
                path, fps=25, class_name="PLAYER", short_track_seconds=1,
                low_confidence=0.25, count_jump=3, worst_limit=5,
            )
            self.assertEqual(report["summary"]["count_jump_events"], 1)
            self.assertEqual(report["largest_count_jumps"][0]["change"], 3)

    def test_rejects_missing_required_columns(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.csv"
            path.write_text("frame,track_id\n0,1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Missing required CSV columns"):
                MODULE.analyze_csv(
                    path, fps=25, class_name=None, short_track_seconds=1,
                    low_confidence=0.25, count_jump=3, worst_limit=5,
                )


if __name__ == "__main__":
    unittest.main()
