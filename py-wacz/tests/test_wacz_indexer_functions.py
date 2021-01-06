import unittest
import tempfile
import os
import zipfile, json, gzip
from wacz.main import main, now
from wacz.waczindexer import WACZIndexer

PAGE_INDEX = "pages/pages.jsonl"


def match_detected_pages(self, detected_pages, passed_pages_url, passed_pages_ts):
    for page in detected_pages:
        page = detected_pages[page]
        url = page["url"]
        ts = page["timestamp"]
        if passed_pages_url == url and passed_pages_ts == None:
            return page
        if passed_pages_url == url and passed_pages_ts == ts:
            return page
    return 0


class TestWaczIndexerFunctions(unittest.TestCase):
    def test_match_detected_page_invalid(self):
        """When passed invalid urls and invalid timestamps the function should return 0"""
        detected_pages = {
            "20201007212236/http://www.example.com/": {
                "url": "http://www.example.com/",
                "timestamp": "20201007212236",
                "title": "Example Domain",
                "rec": "fbt5hqmtseanlxzt",
                "id": "1db0ef709a",
                "text": "Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n",
            }
        }
        self.assertEqual(
            match_detected_pages(self, detected_pages, "fake_url", None), 0
        )
        self.assertEqual(
            match_detected_pages(self, detected_pages, "fake_url", "fake-ts"),
            0,
        )

    def test_match_detected_page_valid(self):
        """When passed valid urls and valid timestamps the function should return the page"""
        detected_pages = {
            "20201007212236/http://www.example.com/": {
                "url": "http://www.example.com/",
                "timestamp": "20201007212236",
                "title": "Example Domain",
                "rec": "fbt5hqmtseanlxzt",
                "id": "1db0ef709a",
                "text": "Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n",
            }
        }
        self.assertEqual(
            match_detected_pages(self, detected_pages, "http://www.example.com/", None),
            {
                "url": "http://www.example.com/",
                "timestamp": "20201007212236",
                "title": "Example Domain",
                "rec": "fbt5hqmtseanlxzt",
                "id": "1db0ef709a",
                "text": "Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n",
            },
        )
        self.assertEqual(
            match_detected_pages(
                self, detected_pages, "http://www.example.com/", "20201007212236"
            ),
            {
                "url": "http://www.example.com/",
                "timestamp": "20201007212236",
                "title": "Example Domain",
                "rec": "fbt5hqmtseanlxzt",
                "id": "1db0ef709a",
                "text": "Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n",
            },
        )


if __name__ == "__main__":
    unittest.main()
