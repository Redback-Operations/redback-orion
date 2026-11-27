import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import analysis_pipeline.run_pipeline as rp
from analysis_pipeline.tracking_json import to_legacy_json

STAGES = ["teams", "movement", "tackles", "workload", "formation"]


def saved_tracks(tmp):
    """Write a tiny tracks.csv and return it with its /tracking JSON, like get_tracks saves."""
    csv_path = Path(tmp) / "tracks.csv"
    csv_path.write_text(
        "frame,track_id,class,confidence,x1,y1,x2,y2\n"
        "0,7,PLAYER,0.9,10,20,30,60\n"
        "1,7,PLAYER,0.9,12,20,32,60\n"
        "1,9,REF,0.8,100,20,120,60\n"
    )
    info = {"fps": 25.0, "width": 1920, "height": 1080, "total_frames": 2,
            "start_frame": 0, "processed_frames": 2,
            "class_names": {0: "PLAYER", 1: "REF"}}
    return csv_path, to_legacy_json(csv_path, info)


def no_detection(*args, **kwargs):
    raise AssertionError("detection ran although saved tracks were passed")


class RunAllTests(unittest.TestCase):
    def run_with_fake_stages(self, failing=None):
        def fake(name):
            def stage(*args):
                if name == failing:
                    raise ValueError("boom")
                return {"stage": name}
            return stage

        patches = [mock.patch.object(rp, "detect_and_track", no_detection)]
        patches += [mock.patch.object(rp, f"stage_{name}", fake(name)) for name in STAGES]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path, tracking = saved_tracks(tmp)
            out = Path(tmp) / "out"
            for p in patches:
                p.start()
            try:
                results = rp.run_all("clip.mp4", out, tracks_csv=csv_path, tracking=tracking)
            finally:
                for p in patches:
                    p.stop()
            written = json.loads((out / "results.json").read_text())
            self.assertTrue((out / "tracking.json").exists())
            self.assertTrue((out / "players.csv").exists())
        return results, written

    def test_saved_tracks_skip_detection_and_run_every_stage(self):
        results, written = self.run_with_fake_stages()

        self.assertEqual(results["processed_frames"], 2)
        self.assertEqual(results["track_ids"], 2)
        self.assertEqual(list(results["stages"]), STAGES)
        self.assertEqual(results["errors"], {})
        self.assertEqual(written, json.loads(json.dumps(results, default=str)))

    def test_failed_stage_is_recorded_and_others_still_run(self):
        results, _ = self.run_with_fake_stages(failing="tackles")

        self.assertEqual(results["errors"], {"tackles": "ValueError: boom"})
        self.assertEqual(list(results["stages"]), [s for s in STAGES if s != "tackles"])


if __name__ == "__main__":
    unittest.main()
