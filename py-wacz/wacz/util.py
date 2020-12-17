import hashlib, datetime, json

WACZ_VERSION = "1.0.0"


def support_hash_file(data):
    """Hashes the passed content using sha256"""
    return hashlib.sha256(data).hexdigest()


def now():
    """Returns the current time"""
    return tuple(datetime.datetime.utcnow().timetuple()[:6])


def validateJSON(jsonData):
    """Attempts to validate a string as json"""
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True


def validate_passed_pages(passed_pages):
    """Validates that a passed pages.jsonl fileis valid json"""

    for i in range(1, len(passed_pages)):
        if validateJSON(passed_pages[i]) == False:
            print("Line %s is not valid JSON" % i)
            return 0
    return 1
