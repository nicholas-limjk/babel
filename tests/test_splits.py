import json
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import create_splits


class SplitGenerationTests(unittest.TestCase):
    def test_create_required_splits(self):
        rows = []
        for book in ["MAT", "MRK", "LUK", "JHN", "ACT"]:
            for verse in range(1, 4):
                rows.append(
                    {
                        "verse_id": f"{book}_001_{verse:03d}",
                        "book": book,
                        "chapter": 1,
                        "verse": verse,
                        "language": "eng",
                        "version": "toy",
                        "text": "text",
                    }
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            verses = root / "verses.csv"
            out = root / "splits"
            with verses.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

            with patch("sys.argv", ["create_splits.py", "--verses", str(verses), "--out", str(out)]):
                create_splits.main()

            mark_only = json.loads((out / "mark_only.json").read_text(encoding="utf-8"))
            self.assertEqual(mark_only["seed_verse_ids"], ["MRK_001_001", "MRK_001_002", "MRK_001_003"])
            self.assertNotIn("MRK_001_001", mark_only["eval_verse_ids"])
            self.assertTrue((out / "seed_50_random_mark.json").exists())
            self.assertTrue((out / "gospels_only.json").exists())


if __name__ == "__main__":
    unittest.main()
