import hashlib, datetime, json
from warcio.timeutils import iso_date_to_timestamp

WACZ_VERSION = "1.0.0"


def support_hash_file(data):
    """Hashes the passed content using sha256"""
    return hashlib.sha256(data).hexdigest()


def construct_passed_pages_dict(passed_content):
    """Creates a dictionary of the passed pages with the url as the key or ts/url if ts is present and the title and text as the values if they have been passed"""
    passed_pages_dict = {}
    for i in range(0, len(passed_content)):
        # Skip the file's header if it's been set
        if "format" not in json.loads(passed_content[i]):
            pages_dict = dict(json.loads(passed_content[i]))

            # Set the default key as url
            key = "%s" % pages_dict["url"]

            # If timestamp is present overwrite the key to be 'ts/url'
            if "ts" in pages_dict:
                key = "%s/%s" % (
                    iso_date_to_timestamp(pages_dict["ts"]),
                    pages_dict["url"],
                )

            # Add the key to the dictionary with a blank value
            passed_pages_dict[key] = {}

            # If title was in the passed pages line add it to the value of the just created dictionary entry
            if "title" in pages_dict:
                passed_pages_dict[key]["title"] = pages_dict["title"]

            # If text was in the passed pages line add it to the value of the just created dictionary entry
            if "text" in pages_dict:
                passed_pages_dict[key]["text"] = pages_dict["text"]

    return passed_pages_dict


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
