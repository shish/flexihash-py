"""
python implementation of Flexihash; all the stuff
in one .py file because it's pretty short
"""
import zlib
import hashlib
import bisect
from typing import List, Tuple, Optional, Any, Dict, Union


Position = Any  # Any orderable type - md5sum (bytes), crc32 (int)
Target = Union[str, bytes]
Resource = Union[str, bytes]


class FlexihashException(Exception):
    pass


class Hasher(object):
    def hash(self, value: Union[Resource, Target]) -> Position:
        raise NotImplementedError()


class Md5Hasher(Hasher):
    def hash(self, value: Union[Resource, Target]) -> Position:
        if hasattr(value, "encode"):
            value = value.encode()
        return hashlib.md5(value).hexdigest()


class Crc32Hasher(Hasher):
    def hash(self, value: Union[Resource, Target]) -> Position:
        if hasattr(value, "encode"):
            value = value.encode()
        return zlib.crc32(value)


class Flexihash(object):
    def __init__(self, hasher: Optional[Hasher] = None, replicas: Optional[int] = None):
        self.replicas = replicas or 64
        self.hasher = hasher or Crc32Hasher()
        self.positionToTarget: Dict[Position, Target] = {}
        self.positionToTargetSorted: List[Tuple[Position, Target]] = []
        self.targetToPositions = {}

    def addTarget(self, target: Target, weight: int = 1) -> "Flexihash":
        if target in self.targetToPositions:
            raise FlexihashException("Target '%s' already exists" % target)

        self.targetToPositions[target] = []

        for i in range(0, self.replicas * weight):
            position = self.hasher.hash(target + str(i))
            self.positionToTarget[position] = target
            self.targetToPositions[target].append(position)

        self.positionToTargetSorted = []

        return self

    def addTargets(self, targets: List[Target]) -> "Flexihash":
        for target in targets:
            self.addTarget(target)

        return self

    def removeTarget(self, target: Target) -> "Flexihash":
        if target not in self.targetToPositions:
            raise FlexihashException("Target '%s' does not exist" % target)

        for position in self.targetToPositions[target]:
            del self.positionToTarget[position]

        del self.targetToPositions[target]

        self.positionToTargetSorted = []

        return self

    def getAllTargets(self) -> List[Target]:
        return sorted(list(self.targetToPositions.keys()))

    def lookup(self, resource: Resource) -> Target:
        targets = self.lookupList(resource, 1)
        if not targets:
            raise FlexihashException("No targets exist")
        return targets[0]

    def lookupList(self, resource: Resource, requestedCount: int) -> List[Target]:
        if not requestedCount:
            raise FlexihashException("Invalid count requested")

        if len(self.targetToPositions) == 0:
            return []

        if len(self.targetToPositions) == 1:
            return [list(self.positionToTarget.values())[0]]

        resourcePosition = self.hasher.hash(resource)

        ptts = self.sortPositionTargets()

        offset = bisect.bisect_left(ptts, (resourcePosition, ""))
        n_targets = len(self.targetToPositions)

        results = []
        for _, value in ptts[offset:] + ptts[:offset]:
            if value not in results:
                results.append(value)

            if len(results) == requestedCount or len(results) == n_targets:
                return results

        return results

    def sortPositionTargets(self) -> List[Tuple[Position, Target]]:
        if not self.positionToTargetSorted:
            self.positionToTargetSorted = sorted(self.positionToTarget.items())
        return self.positionToTargetSorted
