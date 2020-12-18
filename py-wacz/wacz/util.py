import hashlib, datetime, json

WACZ_VERSION = "1.0.0"


def support_hash_file(data):
    """Hashes the passed content using sha256"""
    return hashlib.sha256(data).hexdigest()

def construct_passed_pages_dict(passed_content):
    """Creates a dictionary of the passed pages with the url as the key or ts/url if ts is present and the title and text as the values if they have been passed"""
    passed_pages_dict = {}
    # Skip the first line of the pages.jsonl content as it will be the file's header
    for i in range(0, len(passed_content)):
        if "format" not in json.loads(passed_content[i]):
            pages_json = json.loads(passed_content[i])
            pages_dict = dict(pages_json)

            # Set the default key as url
            key = "%s" % pages_dict["url"]

            # If timestamp is present overwrite the key to be 'ts/url'
            if "ts" in pages_dict:
                key = "%s/%s" % (
                    iso_date_to_timestamp(pages_dict["ts"]),
                    pages_dict["url"],
                )

            #Add the key to the dictionary with a blank value
            passed_pages_dict[key] = {}
            if "title"in pages_dict:
                # If title was in the passed pages line add it to the value of the just created dictionary entry
                passed_pages_dict[key]['title'] = pages_dict['title']
            if "text"in pages_dict:
                # If text was in the passed pages line add it to the value of the just created dictionary entry
                passed_pages_dict[key]['text'] = pages_dict['text']
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


def validate_passed_pages(passed_pages):
    """Validates that a passed pages.jsonl file is valid json"""

    for i in range(1, len(passed_pages)):
        if validateJSON(passed_pages[i]) == False:
            print("Line %s is not valid JSON" % i)
            return 0
    return 1
