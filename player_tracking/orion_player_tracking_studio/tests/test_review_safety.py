import tempfile
import unittest
from pathlib import Path

from review_tool.core import ReviewProject, TrackRow, summarise_tracks


def project():
    p = ReviewProject()
    p.rows = [TrackRow(0, '1', 'PLAYER', .8), TrackRow(5, '1', 'PLAYER', .8),
              TrackRow(3, '2', 'PLAYER', .9), TrackRow(8, '2', 'PLAYER', .9),
              TrackRow(12, '3', 'PLAYER', .9)]
    p.tracks = summarise_tracks(p.rows)
    p.resolve_identities()
    return p


class ReviewSafetyTests(unittest.TestCase):
    def test_overlap_rejection_is_atomic(self):
        p = project()
        with self.assertRaises(ValueError):
            p.merge_tracks(['1', '2'], 'Player 7')
        self.assertEqual(p.manual_merges, {})

    def test_existing_merge_group_is_checked(self):
        p = project()
        p.merge_tracks(['1', '3'], 'Player 7')
        with self.assertRaises(ValueError):
            p.merge_tracks(['2', '3'], 'Player 7')
        self.assertNotIn('2', p.manual_merges)

    def test_conflicting_automatic_ids_stay_distinct(self):
        p = project()
        for key in ('1', '2'):
            p.set_track_value(key, 'team', 'Team 1')
            p.set_track_value(key, 'jumper', '7')
        self.assertNotEqual(p.tracks['1'].stable_id, p.tracks['2'].stable_id)

    def test_export_restores_without_original_csv(self):
        p = project()
        p.set_track_value('1', 'jumper', '7')
        p.merge_tracks(['1', '3'], 'Player 7')
        with tempfile.TemporaryDirectory() as folder:
            saved = p.export(Path(folder))
            restored = ReviewProject.restore(saved['project'])
        self.assertEqual(restored.rows, p.rows)
        self.assertEqual(restored.manual_merges, p.manual_merges)
        self.assertEqual(restored.tracks['1'].jumper, '7')


if __name__ == '__main__':
    unittest.main()
