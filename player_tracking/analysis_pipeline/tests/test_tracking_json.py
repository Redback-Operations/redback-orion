import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis_pipeline.tracking_json import to_legacy_json, write_player_table


class LegacyJsonTests(unittest.TestCase):
    def test_matches_the_shape_the_backend_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "tracks.csv"
            csv_path.write_text(
                "frame,track_id,class,confidence,x1,y1,x2,y2\n"
                "0,7,PLAYER,0.912,10.4,20.6,30.4,60.6\n"
                "2,9,REF,0.5,0,0,10,10\n"
            )
            info = {"fps": 25.0, "width": 1920, "height": 1080, "total_frames": 100,
                    "start_frame": 0, "processed_frames": 3,
                    "class_names": {0: "PLAYER", 1: "REF"}}
            out = to_legacy_json(csv_path, info)

        self.assertEqual(out["video_info"], {"duration": 4.0, "fps": 25,
                                             "total_frames": 100, "resolution": [1920, 1080]})
        frames = out["tracking_results"]
        self.assertEqual([f["frame_number"] for f in frames], [1, 2, 3])
        self.assertEqual(frames[1]["players"], [])
        self.assertEqual(frames[2]["timestamp"], 0.08)
        self.assertEqual(frames[0]["players"][0], {
            "player_id": 7, "team_id": 0, "team_name": "PLAYER",
            "bbox": {"x1": 10, "y1": 20, "x2": 30, "y2": 60},
            "center": {"x": 20, "y": 40}, "confidence": 0.91,
            "width": 20, "height": 40,
        })
        self.assertEqual(frames[2]["players"][0]["team_id"], 1)
        json.dumps(out)  # must be serialisable for the cache


class PlayerTableTests(unittest.TestCase):
    def test_has_the_columns_tackles_workload_and_heatmaps_need(self):
        legacy = {"tracking_results": [{"frame_number": 3, "timestamp": 0.08, "players": [{
            "player_id": 7, "team_id": 0, "team_name": "PLAYER",
            "bbox": {"x1": 10, "y1": 20, "x2": 30, "y2": 60},
            "center": {"x": 20, "y": 40}, "confidence": 0.91, "width": 20, "height": 40,
        }]}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "players.csv"
            write_player_table(legacy, path)
            rows = list(csv.DictReader(open(path)))
        self.assertEqual(rows, [{
            "frame_id": "3", "timestamps_s": "0.08", "timestamp_s": "0.08", "player_id": "7",
            "cx": "20", "cy": "40", "x1": "10", "y1": "20", "x2": "30", "y2": "60",
            "w": "20", "h": "40", "confidence": "0.91",
        }])


if __name__ == "__main__":
    unittest.main()
