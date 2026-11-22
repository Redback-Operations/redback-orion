import sys
import tempfile
import unittest
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))

from tracks import get_tracks, tracks_csv_path


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
        tracks_csv_path(tracks_dir, key).write_text("frame,track_id\n")
        return {"key": key, "tracking_results": []}

    def test_runs_tracking_again_if_the_tracks_csv_is_gone(self):
        result = get_tracks(self.video, self.dir, self.fake_tracking)
        tracks_csv_path(self.dir, result["key"]).unlink()
        get_tracks(self.video, self.dir, self.fake_tracking)
        self.assertEqual(len(self.calls), 2)

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


if __name__ == "__main__":
    unittest.main()
