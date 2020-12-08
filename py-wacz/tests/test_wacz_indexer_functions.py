import unittest
import tempfile
import os
import zipfile, json, gzip
from wacz.main import main, now
from wacz.waczindexer import WACZIndexer

PAGE_INDEX = "pages/pages.jsonl"

class TestWaczIndexerFunctions(unittest.TestCase):
    def test_match_detected_page_invalid(self):
        """When passed invalid urls and invalid timestamps the function should return 0"""
        detected_pages = {'20201007212236/http://www.example.com/': {'url': 'http://www.example.com/', 'timestamp': '20201007212236', 'title': 'Example Domain', 'rec': 'fbt5hqmtseanlxzt', 'id': '1db0ef709a', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'}}
        self.assertEqual(WACZIndexer.match_detected_pages(self, detected_pages, 'fake_url', None), 0)
        self.assertEqual(WACZIndexer.match_detected_pages(self, detected_pages, 'fake_url', 'fake-ts'), 0)

    def test_match_detected_page_valid(self):
        """When passed valid urls and valid timestamps the function should return the page"""
        detected_pages = {'20201007212236/http://www.example.com/': {'url': 'http://www.example.com/', 'timestamp': '20201007212236', 'title': 'Example Domain', 'rec': 'fbt5hqmtseanlxzt', 'id': '1db0ef709a', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'}}
        self.assertEqual(WACZIndexer.match_detected_pages(self, detected_pages, 'http://www.example.com/', None), {'url': 'http://www.example.com/', 'timestamp': '20201007212236', 'title': 'Example Domain', 'rec': 'fbt5hqmtseanlxzt', 'id': '1db0ef709a', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'})
        self.assertEqual(WACZIndexer.match_detected_pages(self, detected_pages, 'http://www.example.com/', '20201007212236'), {'url': 'http://www.example.com/', 'timestamp': '20201007212236', 'title': 'Example Domain', 'rec': 'fbt5hqmtseanlxzt', 'id': '1db0ef709a', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'})

    def test_analyze_passed_pages_valid(self):
        """When passed valid urls and invalid timestamps the function should return the page"""
        detected_pages = {'20201007212236/http://www.example.com/': {'url': 'http://www.example.com/', 'timestamp': '20201007212236', 'title': 'Example Domain', 'rec': 'fbt5hqmtseanlxzt', 'id': '1db0ef709a', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'}}
        index = WACZIndexer('output', 'input')
        index.pages = detected_pages
        passed_pages = ['{"format": "json-pages-1.0", "id": "pages", "title": "All Pages"}', '{"id": "1db0ef709a", "url": "http://www.example.com/", "ts": "2020-10-07T21:22:36Z", "title": "Example Domain"}']
        r = index.analyze_passed_pages(PAGE_INDEX, passed_pages)
        self.assertEqual(index.analyze_passed_pages(PAGE_INDEX, passed_pages), {'20201007212236/http://www.example.com/': {'timestamp': '20201007212236', 'url': 'http://www.example.com/', 'title': 'http://www.example.com/', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'}})
        self.assertTrue(index.has_text)

    def test_analyze_passed_pages_invalid(self):
        """When passed invalid urls the function should return 0"""
        detected_pages = {'20201007212236/http://www.example.com/': {'url': 'http://www.example.com/', 'timestamp': '20201007212236', 'title': 'Example Domain', 'rec': 'fbt5hqmtseanlxzt', 'id': '1db0ef709a', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'}}
        index = WACZIndexer('output', 'input')
        index.pages = detected_pages
        passed_pages = ['{"format": "json-pages-1.0", "id": "pages", "title": "All Pages"}', '{"id": "1db0ef709a", "url": "http://www.fake.com/", "ts": "2020-10-07T21:22:36Z", "title": "Example Domain"}']
        r = index.analyze_passed_pages(PAGE_INDEX, passed_pages)
        self.assertEqual(index.analyze_passed_pages(PAGE_INDEX, passed_pages), 0)

    def test_analyze_passed_pages_invalid(self):
        """When passed invalid urls and invalid timestamps the function should return 0"""
        detected_pages = {'20201007212236/http://www.example.com/': {'url': 'http://www.example.com/', 'timestamp': '20201007212236', 'title': 'Example Domain', 'rec': 'fbt5hqmtseanlxzt', 'id': '1db0ef709a', 'text': 'Example Domain\nThis domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\n'}}
        index = WACZIndexer('output', 'input')
        index.pages = detected_pages
        passed_pages = ['{"format": "json-pages-1.0", "id": "pages", "title": "All Pages"}', '{"id": "1db0ef709a", "url": "http://www.fake.com/", "title": "Example Domain"}']
        self.assertEqual(index.analyze_passed_pages(PAGE_INDEX, passed_pages), 0)

if __name__ == "__main__":
    unittest.main()
