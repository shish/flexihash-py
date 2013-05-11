import hashlib


class Md5Hasher(object):
    def hash(self, value):
        return hashlib.md5(value).hexdigest()
