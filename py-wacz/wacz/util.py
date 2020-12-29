import hashlib, datetime

WACZ_VERSION = "1.0.0"


def support_hash_file(hash_type, data):
    """Hashes the passed content using sha256 or md5"""
    if hash_type == "sha256":
        return hashlib.sha256(data).hexdigest()
    if hash_type == "md5":
        return hashlib.md5(data).hexdigest()


def now():
    return tuple(datetime.datetime.utcnow().timetuple()[:6])
