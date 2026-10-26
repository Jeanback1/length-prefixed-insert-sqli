import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "poc"))

from wrap import MAX_BODY, collapse_chr, wrap


class WrapTests(unittest.TestCase):
    def test_length_header_matches_the_body(self):
        self.assertEqual(wrap("abc"), "v1|0003|abc")

    def test_length_counts_bytes(self):
        self.assertEqual(wrap("á"), "v1|0002|á")

    def test_chr_chain_shrinks_under_the_budget(self):
        exploded = "||".join(["CHR(65)"] * 40)
        self.assertGreater(len(exploded), MAX_BODY)
        collapsed = collapse_chr(exploded)
        self.assertEqual(collapsed, "'" + ("A" * 40) + "'")
        self.assertLessEqual(len(collapsed.encode()), MAX_BODY)
        wrap(collapsed)
        with self.assertRaises(ValueError):
            wrap(exploded)

    def test_quotes_inside_a_chr_literal_are_escaped(self):
        self.assertEqual(collapse_chr("CHR(39)"), "''''")


if __name__ == "__main__":
    unittest.main()
