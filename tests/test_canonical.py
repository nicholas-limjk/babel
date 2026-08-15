import unittest

from abtm.canonical import make_verse_id, norm_book, parse_verse_id, verse_sort_key


class CanonicalVerseTests(unittest.TestCase):
    def test_normalizes_common_book_names(self):
        self.assertEqual(norm_book("Mark"), "MRK")
        self.assertEqual(norm_book("1 John"), "1JN")
        self.assertEqual(norm_book("Song_of_Songs"), "SNG")

    def test_make_and_parse_verse_id(self):
        verse_id = make_verse_id("John", 3, 16)
        self.assertEqual(verse_id, "JHN_003_016")
        ref = parse_verse_id(verse_id)
        self.assertEqual((ref.book, ref.chapter, ref.verse), ("JHN", 3, 16))

    def test_sort_key_uses_canonical_order(self):
        self.assertLess(verse_sort_key("MAT_001_001"), verse_sort_key("MRK_001_001"))


if __name__ == "__main__":
    unittest.main()
