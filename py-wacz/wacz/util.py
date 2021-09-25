import hashlib, datetime, json
from warcio.timeutils import iso_date_to_timestamp
import pkg_resources

WACZ_VERSION = "1.1.1"


def check_http_and_https(url, ts, pages_dict):
    """Checks for http and https versions of the passed url
    in the pages dict
    :param url to check, pages_dict the user passed
    :returns: True or False depending on if a match was found
    :rtype: boolean
    """
    url_body = url.split(":")[1]
    checks = [
        f"http:{url_body}",
        f"https:{url_body}",
        f"{ts}/http:{url_body}",
        f"{ts}/https:{url_body}",
    ]

    for check in checks:
        if check in pages_dict:
            return check

    return ""


def get_py_wacz_version():
    """Get version of the py-wacz package"""
    return pkg_resources.get_distribution("wacz").version


def support_hash_file(hash_type, data):
    """Hashes the passed content using sha256 or md5"""
    if hash_type == "sha256":
        return "sha256:%s" % hashlib.sha256(data).hexdigest()
    if hash_type == "md5":
        return "md5:%s" % hashlib.md5(data).hexdigest()


def construct_passed_pages_dict(passed_content):
    """Creates a dictionary of the passed pages with the url as the key or ts/url if ts is present and the title and text as the values if they have been passed"""
    passed_pages_dict = {}
    for i in range(0, len(passed_content)):
        # Skip the file's header if it's been set
        header = json.loads(passed_content[i])
        if "format" not in header:
            pages_dict = dict(header)
            url = pages_dict.pop("url", "")

            # Set the default key as url
            key = url

            # If timestamp is present overwrite the key to be 'ts/url'
            if "ts" in pages_dict:
                key = iso_date_to_timestamp(pages_dict.pop("ts")) + "/" + url

            # Add the key to the dictionary with remaining data
            passed_pages_dict[key] = pages_dict

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
