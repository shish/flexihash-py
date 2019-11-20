import unittest

from flexihash import Crc32Hasher, Md5Hasher


class HasherTest(unittest.TestCase):
    def test_Crc32Hash(self):
        hasher = Crc32Hasher()
        result1 = hasher.hash("test")
        result2 = hasher.hash("test")
        result3 = hasher.hash("different")

        self.assertEqual(result1, result2)
        self.assertNotEqual(result1, result3)  # fragile but worthwhile

    def test_Md5Hash(self):
        hasher = Md5Hasher()
        result1 = hasher.hash("test")
        result2 = hasher.hash("test")
        result3 = hasher.hash("different")

        self.assertEqual(result1, result2)
        self.assertNotEqual(result1, result3)  # fragile but worthwhile
