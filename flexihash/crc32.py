import zlib

class Flexihash_Crc32Hasher(object):
    def hash(self, value):
        return zlib.crc32(value)
