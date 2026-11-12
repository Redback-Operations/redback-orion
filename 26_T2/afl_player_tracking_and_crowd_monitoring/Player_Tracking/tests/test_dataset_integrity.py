"""Regression tests for the incomplete-download and review-export failures."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import yaml
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from dataset_integrity import audit_yaml, read_pairs
from smart_labeller import SmartLabeller, Box
import build_datasets
import train


class DatasetIntegrityTests(unittest.TestCase):
    def pair(self, root, name="frame", label="0 0.5 0.5 0.2 0.3\n", image=b"image"):
        (root / "images").mkdir(parents=True, exist_ok=True)
        (root / "labels").mkdir(parents=True, exist_ok=True)
        (root / "images" / f"{name}.jpg").write_bytes(image)
        if label is not None:
            (root / "labels" / f"{name}.txt").write_text(label)

    def test_missing_label_is_not_a_background(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair(root, label=None)
            with self.assertRaisesRegex(ValueError, "1 missing label"):
                read_pairs(root, 2)
            (root / "labels/frame.txt").write_text("")
            self.assertEqual(read_pairs(root, 2)[0][1], [])

    def test_orphan_labels_and_invalid_classes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair(root, label="2 0.5 0.5 0.2 0.3")
            with self.assertRaisesRegex(ValueError, "Invalid YOLO"):
                read_pairs(root, 2)
            (root / "labels/orphan.txt").write_text("")
            with self.assertRaisesRegex(ValueError, "1 labels without images"):
                read_pairs(root, 2)

    def test_renamed_image_cannot_leak_into_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair(root / "train", name="a")
            self.pair(root / "val", name="b")
            config = root / "data.yaml"
            config.write_text(yaml.safe_dump({"path": str(root), "train": "train/images",
                                              "val": "val/images", "names": ["PLAYER", "REF"]}))
            with self.assertRaisesRegex(ValueError, "leakage"):
                audit_yaml(config)
            (root / "val/images/b.jpg").write_bytes(b"different image")
            self.assertEqual(len(audit_yaml(config)["splits"]["train"]), 1)

    def test_incomplete_raw_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(build_datasets, "RAW", Path(tmp)):
            self.pair(Path(tmp) / "gcs_vs_car")
            with self.assertRaisesRegex(ValueError, "expected at least 200"):
                build_datasets.load_pairs("gcs_vs_car")

    def test_fine_tune_preserves_checkpoint_classes_and_explicit_learning_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair(root / "train", image=b"train")
            self.pair(root / "val", image=b"val")
            config = root / "data.yaml"
            config.write_text(yaml.safe_dump({"path": str(root), "train": "train/images",
                                              "val": "val/images", "names": ["PLAYER", "REF"]}))
            model = MagicMock(names={0: "PLAYER", 1: "REF"})
            with patch.object(sys, "argv", ["train.py", "--data", str(config), "--fine-tune"]), \
                    patch("ultralytics.YOLO", return_value=model) as factory:
                train.main()
            self.assertTrue(factory.call_args.args[0].endswith("models/player_ref_best.pt"))
            self.assertEqual(model.train.call_args.kwargs["optimizer"], "AdamW")
            self.assertEqual(model.train.call_args.kwargs["lr0"], 0.0001)
            self.assertEqual(model.train.call_args.kwargs["patience"], 20)
            model.names = {0: "person"}
            model.train.reset_mock()
            with patch.object(sys, "argv", ["train.py", "--data", str(config), "--fine-tune"]), \
                    patch("ultralytics.YOLO", return_value=model), \
                    self.assertRaisesRegex(SystemExit, "matching classes"):
                train.main()
            model.train.assert_not_called()

    def labeller(self, root):
        lab = SmartLabeller.__new__(SmartLabeller)
        lab.video_name = "match"
        lab.labels_dir, lab.images_dir = root / "labels", root / "images"
        lab.frame_idx = 60
        lab.frame = np.zeros((20, 20, 3), dtype=np.uint8)
        lab.width = lab.height = 20
        lab.save_images = True
        lab._reviewed = set()
        lab.annotations = {"match": {60: [Box(1, 2, 2, 10, 18)]}}
        return lab

    def test_review_saves_edits_and_empty_negative_before_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair(root, "match_frame_000060")
            lab = self.labeller(root)
            lab._mark_reviewed(60)
            label = root / "labels/match_frame_000060.txt"
            self.assertTrue(label.read_text().startswith("1 "))
            self.assertEqual((root / "reviewed.txt").read_text(), "60\n")
            lab.annotations["match"][60] = []
            lab._mark_reviewed(60)
            self.assertEqual(label.read_text(), "")

    def test_revoked_frame_is_removed_from_reviewed_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.pair(root, "match_frame_000060")
            lab = self.labeller(root)
            lab._reviewed = {60}
            lab._run_split()
            exported = root / "reviewed/images/match_frame_000060.jpg"
            self.assertTrue(exported.exists())
            lab._reviewed.clear()
            lab._run_split()
            self.assertFalse(exported.exists())
            self.assertTrue((root / "unreviewed/images/match_frame_000060.jpg").exists())
            self.assertNotIn("val", yaml.safe_load((root / "reviewed/data.yaml").read_text()))

    def test_broadcast_holdout_uses_manifest_and_temporal_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "match/reviewed"
            frames = list(range(0, 1200, 60))
            for frame in frames:
                self.pair(folder, f"match_frame_{frame:06d}", image=str(frame).encode())
            (folder.parent / "reviewed.txt").write_text("\n".join(map(str, frames)))
            old = {}
            for ds in build_datasets.RAW_CLASSES:
                self.pair(root / ds, image=ds.encode())
                old[ds] = read_pairs(root / ds, len(build_datasets.RAW_CLASSES[ds]))
            with patch.object(build_datasets, "OUT", root / "out"):
                build_datasets.build_broadcast(old, [folder], "clean", 300)
                train = list((root / "out/clean/train/images").glob("match*"))
                val = list((root / "out/clean/val/images").glob("match*"))
                self.assertEqual(len(val), 4)
                self.assertGreater(min(int(p.stem.rsplit("_", 1)[1]) for p in val) -
                                   max(int(p.stem.rsplit("_", 1)[1]) for p in train), 300)
                (folder.parent / "reviewed.txt").write_text("60\n")
                with self.assertRaisesRegex(ValueError, "Unreviewed/stale"):
                    build_datasets.build_broadcast(old, [folder], "reject", 300)
                self.assertFalse((root / "out/reject").exists())


if __name__ == "__main__":
    unittest.main()
