import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis_pipeline.tackle_detection import detect_tackles


def crowd(frames, players, spacing):
    """Players standing `spacing` pixels apart in a row, for each frame."""
    rows = []
    for frame in frames:
        for pid in range(players):
            cx, cy = 100 + pid * spacing, 200
            rows.append({"frame_id": frame, "player_id": pid, "cx": cx, "cy": cy,
                         "x1": cx - 10, "y1": cy - 30, "x2": cx + 10, "y2": cy + 30,
                         "timestamps_s": frame / 25})
    return pd.DataFrame(rows)


class TackleDetectionTests(unittest.TestCase):
    def test_a_tight_group_held_for_several_frames_is_one_event(self):
        _, events = detect_tackles(crowd(range(10), players=6, spacing=20))
        self.assertEqual(len(events), 1)
        self.assertEqual((events[0]["start_frame"], events[0]["end_frame"]), (0, 9))
        self.assertEqual(events[0]["players_involved"], 6)

    def test_spread_out_players_are_not_a_tackle(self):
        _, events = detect_tackles(crowd(range(10), players=6, spacing=200))
        self.assertEqual(events, [])

    def test_too_short_a_group_is_ignored(self):
        _, events = detect_tackles(crowd(range(3), players=6, spacing=20))
        self.assertEqual(events, [])

    def test_missing_columns_raise(self):
        with self.assertRaises(ValueError):
            detect_tackles(pd.DataFrame({"frame_id": [1]}))


if __name__ == "__main__":
    unittest.main()
