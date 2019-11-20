import zlib
import hashlib
import bisect


class FlexihashException(Exception):
    pass


class Hasher(object):
    def hash(self, value):
        raise NotImplementedError()


class Md5Hasher(Hasher):
    def hash(self, value):
        if hasattr(value, "encode"):
            value = value.encode()
        return hashlib.md5(value).hexdigest()


class Crc32Hasher(Hasher):
    def hash(self, value):
        if hasattr(value, "encode"):
            value = value.encode()
        return zlib.crc32(value)


class Flexihash(object):
    def __init__(self, hasher=None, replicas=None):
        self.replicas = replicas or 64
        self.hasher = hasher or Crc32Hasher()
        self.targetCount = 0
        self.positionToTarget = {}
        self.positionToTargetSorted = []
        self.targetToPositions = {}

    def addTarget(self, target, weight=1):
        if target in self.targetToPositions:
            raise FlexihashException("Target '%s' already exists" % target)

        self.targetToPositions[target] = []

        for i in range(0, self.replicas * weight):
            position = self.hasher.hash(target + str(i))
            self.positionToTarget[position] = target
            self.targetToPositions[target].append(position)

        self.positionToTargetSorted = []
        self.targetCount = self.targetCount + 1

        return self

    def addTargets(self, targets):
        for target in targets:
            self.addTarget(target)

        return self

    def removeTarget(self, target):
        if target not in self.targetToPositions:
            raise FlexihashException("Target '%s' does not exist" % target)

        for position in self.targetToPositions[target]:
            del self.positionToTarget[position]

        del self.targetToPositions[target]

        self.positionToTargetSorted = []
        self.targetCount = self.targetCount - 1

        return self

    def getAllTargets(self):
        return sorted(list(self.targetToPositions.keys()))

    def lookup(self, resource):
        targets = self.lookupList(resource, 1)
        if not targets:
            raise FlexihashException("No targets exist")
        return targets[0]

    def lookupList(self, resource, requestedCount):
        if not requestedCount:
            raise FlexihashException("Invalid count requested")

        if not self.positionToTarget:
            return []

        if self.targetCount == 1:
            return [
                list(self.positionToTarget.values())[0],
            ]

        resourcePosition = self.hasher.hash(resource)

        results = []
        collect = False

        self.sortPositionTargets()

        offset = bisect.bisect_left(self.positionToTargetSorted, (resourcePosition, ""))

        for key, value in self.positionToTargetSorted[offset:]:
            if not collect and key > resourcePosition:
                collect = True

            if collect and value not in results:
                results.append(value)

            if len(results) == requestedCount or len(results) == self.targetCount:
                return results

        for key, value in self.positionToTargetSorted:
            if value not in results:
                results.append(value)

            if len(results) == requestedCount or len(results) == self.targetCount:
                return results

        return results

    # def __str__(self):

    def sortPositionTargets(self):
        if not self.positionToTargetSorted:
            self.positionToTargetSorted = sorted(self.positionToTarget.items())
