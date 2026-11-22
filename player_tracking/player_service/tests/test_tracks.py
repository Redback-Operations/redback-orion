import json
import sys
import tempfile
import unittest
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))

from tracks import get_tracks, to_legacy_json


class GetTracksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.video = self.dir / "clip.mp4"
        self.video.write_bytes(b"video bytes")
        self.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def fake_tracking(self, video_path, tracks_dir, key):
        self.calls.append(key)
        return {"key": key, "tracking_results": []}

    def test_runs_tracking_when_nothing_is_saved(self):
        result = get_tracks(self.video, self.dir, self.fake_tracking)
        self.assertEqual(len(self.calls), 1)
        self.assertTrue((self.dir / f"{result['key']}.json").exists())

    def test_reuses_saved_result_for_the_same_file(self):
        first = get_tracks(self.video, self.dir, self.fake_tracking)
        copy = self.dir / "renamed_upload.mp4"
        copy.write_bytes(self.video.read_bytes())
        second = get_tracks(copy, self.dir, self.fake_tracking)
        self.assertEqual(first, second)
        self.assertEqual(len(self.calls), 1)

    def test_different_file_runs_tracking_again(self):
        get_tracks(self.video, self.dir, self.fake_tracking)
        other = self.dir / "other.mp4"
        other.write_bytes(b"different video")
        get_tracks(other, self.dir, self.fake_tracking)
        self.assertEqual(len(self.calls), 2)

    def test_failed_tracking_saves_nothing(self):
        def broken(video_path, tracks_dir, key):
            raise RuntimeError("model crashed")

        with self.assertRaises(RuntimeError):
            get_tracks(self.video, self.dir, broken)
        self.assertEqual(list(self.dir.glob("*.json*")), [])
        get_tracks(self.video, self.dir, self.fake_tracking)
        self.assertEqual(len(self.calls), 1)


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


if __name__ == "__main__":
    unittest.main()
