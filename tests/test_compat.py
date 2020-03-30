import unittest

from hashlib import md5
from flexihash import Flexihash


class TestCompatibility(unittest.TestCase):
    """
    Make sure that this version gives the same
    results for the same input as the original
    """

    def test_lots(self):
        # generate lots of test cases, and use md5 to be "random" in case
        # a fast hasher (eg crc) doesn't distribute data well
        fh = Flexihash()

        results = {}
        for n in "abcdefghij":
            n = md5(str(n).encode()).hexdigest()
            fh.addTarget(n)
            results[n] = 0
        for n in range(0, 1000):
            n = md5(str(n).encode()).hexdigest()
            results[fh.lookup(str(n))] += 1

        self.assertEqual(
            results,
            {
                "0cc175b9c0f1b6a831c399e269772661": 105,
                "2510c39011c5be704182423e3a695e91": 54,
                "363b122c528f54df4a0446b6bab05515": 113,
                "4a8a08f09d37b73795649038408b5f33": 119,
                "8277e0910d750195b448797616e091ad": 168,
                "865c0c0b4ab0e063e5caa3387c1a8741": 74,
                "8fa14cdd754f91cc6554c9e71929cce7": 94,
                "92eb5ffee6ae2fec3ad71c777531578f": 63,
                "b2f5ff47436671b6e533d8dc3614845d": 124,
                "e1671797c52e15f763380b45e841ec32": 86,
            },
        )
