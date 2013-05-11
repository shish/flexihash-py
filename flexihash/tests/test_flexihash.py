import unittest2

from flexihash import Flexihash, Flexihash_Exception


class TestFlexihash(unittest2.TestCase):

    def testLookupThrowsExceptionOnEmpty(self):
        hashSpace = Flexihash()
        self.assertRaises(Flexihash_Exception, hashSpace.lookup, 'test')

    def testLookupListThrowsExceptionOnZero(self):
        hashSpace = Flexihash()
        self.assertRaises(Flexihash_Exception, hashSpace.lookupList, 'test', 0)

    def testLookupListReturnsWithShortListIfAllTargetsUsed(self):
        hashSpace = Flexihash()
        # both have CRC32 of 1253617450
        hashSpace.addTarget("x").addTarget("y")     # make the list non-empty, non-one-value, to avoid shortcuts
        hashSpace.addTarget("80726")                # add a value
        hashSpace.addTarget("14746907")             # add a different value with the same hash, to clobber the first
        hashSpace.removeTarget("14746907")          # remove the fourth value; with the third clobbered, only X and Y are left
        result = hashSpace.lookupList('test', 3)    # try to get 3 results, our target list is X, Y, 80726
        self.assertEqual(len(result), 2)            # but 80726 isn't reachable since it was clobbered
        self.assertIn("x", result)                  # all that's left is x
        self.assertIn("y", result)                  # and y

    def testGetAllTargetsEmpty(self):
        hashSpace = Flexihash()
        self.assertEqual(hashSpace.getAllTargets(), [])

    def testAddTargetThrowsExceptionOnDuplicateTarget(self):
        hashSpace = Flexihash()
        hashSpace.addTarget('t-a')
        self.assertRaises(Flexihash_Exception, hashSpace.addTarget, 't-a')

    def testAddTargetAndGetAllTargets(self):
        hashSpace = Flexihash()
        hashSpace \
            .addTarget('t-a') \
            .addTarget('t-b') \
            .addTarget('t-c')

        self.assertEqual(hashSpace.getAllTargets(), ['t-a', 't-b', 't-c'])

    def testAddTargetsAndGetAllTargets(self):
        targets = ['t-a', 't-b', 't-c']

        hashSpace = Flexihash()
        hashSpace.addTargets(targets)
        self.assertEqual(hashSpace.getAllTargets(), targets)

    def testRemoveTarget(self):
        hashSpace = Flexihash()
        hashSpace \
            .addTarget('t-a') \
            .addTarget('t-b') \
            .addTarget('t-c') \
            .removeTarget('t-b')

        self.assertEqual(hashSpace.getAllTargets(), ['t-a', 't-c'])

    def testRemoveTargetFailsOnMissingTarget(self):
        hashSpace = Flexihash()
        self.assertRaises(Flexihash_Exception, hashSpace.removeTarget, 'not-there')

    def testHashSpaceRepeatableLookups(self):
        hashSpace = Flexihash()
        for i in range(1,10):
            hashSpace.addTarget("target" + str(i))

        self.assertEqual(hashSpace.lookup('t1'), hashSpace.lookup('t1'))
        self.assertEqual(hashSpace.lookup('t2'), hashSpace.lookup('t2'))

    def testHashSpaceLookupsAreValidTargets(self):
        targets = ["target"+str(i) for i in range(1, 10)]

        hashSpace = Flexihash()
        hashSpace.addTargets(targets)

        for i in range(1, 10):
            self.assertTrue(hashSpace.lookup("r"+str(i)) in targets, 'target must be in list of targets')

    def testHashSpaceConsistentLookupsAfterAddingAndRemoving(self):
        hashSpace = Flexihash()
        for i in range(1,10):
            hashSpace.addTarget("target" + str(i))

        results1 = []
        for i in range(1,100):
            results1.append(hashSpace.lookup("t"+str(i)))

        hashSpace \
            .addTarget('new-target') \
            .removeTarget('new-target') \
            .addTarget('new-target') \
            .removeTarget('new-target')

        results2 = []
        for i in range(1,100):
            results2.append(hashSpace.lookup("t"+str(i)))

        # This is probably optimistic, as adding/removing a target may
        # clobber existing targets and is not expected to restore them.
        self.assertEqual(results1, results2)

    def testHashSpaceConsistentLookupsWithNewInstance(self):
        hashSpace1 = Flexihash()
        for i in range(1,10):
            hashSpace1.addTarget("target" + str(i))

        results1 = []
        for i in range(1,100):
            results1.append(hashSpace1.lookup("t"+str(i)))

        hashSpace2 = Flexihash()
        for i in range(1,10):
            hashSpace2.addTarget("target" + str(i))

        results2 = []
        for i in range(1,100):
            results2.append(hashSpace2.lookup("t"+str(i)))

        self.assertEqual(results1, results2)

    def testGetMultipleTargets(self):
        hashSpace = Flexihash()
        for i in range(1,10):
            hashSpace.addTarget("target" + str(i))

        targets = hashSpace.lookupList('resource', 2)

        self.assertIsInstance(targets, list)
        self.assertEqual(len(targets), 2)
        self.assertNotEqual(targets[0], targets[1])

    def testGetMultipleTargetsWithOnlyOneTarget(self):
        hashSpace = Flexihash()
        hashSpace.addTarget("single-target")

        targets = hashSpace.lookupList('resource', 2)

        self.assertIsInstance(targets, list)
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0], 'single-target')

    def testGetMoreTargetsThanExist(self):
        hashSpace = Flexihash()
        hashSpace.addTarget("target1")
        hashSpace.addTarget("target2")

        targets = hashSpace.lookupList('resource', 4)

        self.assertIsInstance(targets, list)
        self.assertEqual(len(targets), 2)
        self.assertNotEqual(targets[0], targets[1])

    def testGetMultipleTargetsNeedingToLoopToStart(self):
        mockHasher = MockHasher()
        hashSpace = Flexihash(mockHasher, 1)

        mockHasher.setHashValue(10)
        hashSpace.addTarget("t1")

        mockHasher.setHashValue(20)
        hashSpace.addTarget("t2")

        mockHasher.setHashValue(30)
        hashSpace.addTarget("t3")

        mockHasher.setHashValue(40)
        hashSpace.addTarget("t4")

        mockHasher.setHashValue(50)
        hashSpace.addTarget("t5")

        mockHasher.setHashValue(35)
        targets = hashSpace.lookupList('resource', 4)

        self.assertEqual(targets, ['t4', 't5', 't1', 't2'])

    def testGetMultipleTargetsWithoutGettingAnyBeforeLoopToStart(self):
        mockHasher = MockHasher()
        hashSpace = Flexihash(mockHasher, 1)

        mockHasher.setHashValue(10)
        hashSpace.addTarget("t1")

        mockHasher.setHashValue(20)
        hashSpace.addTarget("t2")

        mockHasher.setHashValue(30)
        hashSpace.addTarget("t3")

        mockHasher.setHashValue(100)
        targets = hashSpace.lookupList('resource', 2)

        self.assertEqual(targets, ['t1', 't2'])

    def testGetMultipleTargetsWithoutNeedingToLoopToStart(self):
        mockHasher = MockHasher()
        hashSpace = Flexihash(mockHasher, 1)

        mockHasher.setHashValue(10)
        hashSpace.addTarget("t1")

        mockHasher.setHashValue(20)
        hashSpace.addTarget("t2")

        mockHasher.setHashValue(30)
        hashSpace.addTarget("t3")

        mockHasher.setHashValue(15)
        targets = hashSpace.lookupList('resource', 2)

        self.assertEqual(targets, ['t2', 't3'])

    def testFallbackPrecedenceWhenServerRemoved(self):
        mockHasher = MockHasher()
        hashSpace = Flexihash(mockHasher, 1)

        mockHasher.setHashValue(10)
        hashSpace.addTarget("t1")

        mockHasher.setHashValue(20)
        hashSpace.addTarget("t2")

        mockHasher.setHashValue(30)
        hashSpace.addTarget("t3")

        mockHasher.setHashValue(15)

        self.assertEqual(hashSpace.lookup('resource'), 't2')
        self.assertEqual(
            hashSpace.lookupList('resource', 3),
            ['t2', 't3', 't1']
        )

        hashSpace.removeTarget('t2')

        self.assertEqual(hashSpace.lookup('resource'), 't3')
        self.assertEqual(
            hashSpace.lookupList('resource', 3),
            ['t3', 't1']
        )

        hashSpace.removeTarget('t3')

        self.assertEqual(hashSpace.lookup('resource'), 't1')
        self.assertEqual(
            hashSpace.lookupList('resource', 3),
            ['t1']
        )

class MockHasher(object):  # Hasher):
    def setHashValue(self, hash):
        self._hashValue = hash

    def hash(self, value):
        return self._hashValue
