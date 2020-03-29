import unittest

from flexihash import Crc32Hasher, Md5Hasher, Hasher


class HasherTest(unittest.TestCase):
    def test_BaseHahser(self):
        hasher = Hasher()
        with self.assertRaises(NotImplementedError):
            hasher.hash("test")

    def test_Crc32Hash(self):
        hasher = Crc32Hasher()
        self.assertEqual(hasher.hash("test"), 3632233996)
        self.assertEqual(hasher.hash("test"), 3632233996)
        self.assertEqual(hasher.hash("different"), 1812431075)

    def test_Md5Hash(self):
        hasher = Md5Hasher()
        self.assertEqual(hasher.hash("test"), "098f6bcd4621d373cade4e832627b4f6")
        self.assertEqual(hasher.hash("test"), "098f6bcd4621d373cade4e832627b4f6")
        self.assertEqual(hasher.hash("different"), "29e4b66fa8076de4d7a26c727b8dbdfa")
