from .crc32 import Crc32Hasher
from .exc import Flexihash_Exception


class Flexihash(object):
    def __init__(self, hasher=None, replicas=None):
        self.replicas = replicas or 64
        self.hasher = hasher or Crc32Hasher()
        self.targetCount = 0
        self.positionToTarget = {}
        self.targetToPositions = {}
        self.positionToTargetSorted = False

    def addTarget(self, target, weight=1):
        if target in self.targetToPositions:
            raise Flexihash_Exception("Target '%s' already exists" % target)

        self.targetToPositions[target] = []

        for i in range(0, self.replicas * weight):
            position = self.hasher.hash(target + str(i))
            self.positionToTarget[position] = target
            self.targetToPositions[target].append(position)

        self.pisitionToTargetSorted = False
        self.targetCount = self.targetCount + 1

        return self

    def addTargets(self, targets):
        for target in targets:
            self.addTarget(target)

        return self

    def removeTarget(self, target):
        if target not in self.targetToPositions:
            raise Flexihash_Exception("Target '%s' does not exist" % target)

        for position in self.targetToPositions[target]:
            del self.positionToTarget[position]

        del self.targetToPositions[target]

        self.targetCount = self.targetCount - 1

        return self

    def getAllTargets(self):
        return self.targetToPositions.keys()

    def lookup(self, resource):
        targets = self.lookupList(resource, 1)
        if not targets:
            raise Flexihash_Exception("No targets exist")
        return targets[0]

    def lookupList(self, resource, requestedCount):
        if not requestedCount:
            raise Flexihash_Exception("Invalid count requested")

        if not self.positionToTarget:
            return []

        #if this.targetCount == 1:
        #    return array_unique(array_values(this.positionToTarget))

        resourcePosition = self.hasher.hash(resource)

        results = []
        collect = False

        self.sortPositionTargets()

        for key, value in sorted(self.positionToTarget.items()):
            if not collect and key > resourcePosition:
                collect = True

            if collect and value not in results:
                results.append(value)

            if len(results) == requestedCount or len(results) == self.targetCount:
                return results

        for key, value in sorted(self.positionToTarget.items()):
            if value not in results:
                results.append(value)

            if len(results) == requestedCount or len(results) == self.targetCount:
                return results

        return results

    #def __str__(self):

    def sortPositionTargets(self):
        if not self.positionToTargetSorted:
            #sort(self.positionToTargetSorted)
            self.positionToTargetSorted = True

