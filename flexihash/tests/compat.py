import unittest2

from flexihash import Flexihash


class TestCompat(unittest2.TestCase):
    """
    Make sure that this version gives the same
    results for the same input as the original
    """
    def test_basic(self):
        fh = Flexihash()

        fh.addTarget("a")
        fh.addTarget("b")
        fh.addTarget("c")

        self.assertEqual(fh.lookup("1"), "a")
        self.assertEqual(fh.lookup("2"), "b")
        self.assertEqual(fh.lookup("3"), "a")
