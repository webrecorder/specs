import unittest
import tempfile
import os
import zipfile, json, gzip,hashlib
from wacz.util import support_hash_file, validateJSON, validate_passed_pages

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestUtilFunctions(unittest.TestCase):

    def test_util_hash(self):
        """When invoking the util hash method a sha 256 hash should be returned"""
        test_hash = hashlib.sha256('test'.encode('utf-8')).hexdigest()
        self.assertEqual(support_hash_file('test'.encode('utf-8')), test_hash)

    def test_util_validate_json_succeed(self):
        """validate json method should succed with valid json"""
        self.assertTrue(validateJSON('{"test": "test"}'))

    def test_util_validate_json_fail(self):
        """validate json method should fail with valid json"""
        self.assertFalse(validateJSON('test": "test"}'))

    def test_util_validate_passed_pages(self):
        """validate_passed_pages should return 1 if the passed pages are valid"""
        passed_pages_valid = [
            '{"format": "json-pages-1.0", "id": "pages", "title": "All Pages", "hasText": true}',
            '{"id": "nMPmELqfFP8erKRXHeZgSa", "url": "https://test/", "ts": "2020-12-07T14:34:44Z", "title": "https://test/", "text": "test"}'
            ]

        self.assertEqual(validate_passed_pages(passed_pages_valid), 1)

    def test_util_validate_passed_pages_invalid(self):
        """validate_passed_pages should return 0 if the passed pages are invalid json"""
        passed_pages_valid = [
            '{"format": "json-pages-1.0", "id": "pages", "title": "All Pages", "hasText": true}',
            '{"s://test/", "ts": "2020-12-07T14:34:44Z", "title": "https://test/", "text": "test"}'
            ]

        self.assertEqual(validate_passed_pages(passed_pages_valid), 0)

    def test_util_validate_passed_pages_invalid_header(self):
        """validate_passed_pages should return 0 if the passed pages have an invalid header"""
        passed_pages_missing_format = [
            '{"id": "pages", "title": "All Pages", "hasText": true}',
            '{"s://test/", "ts": "2020-12-07T14:34:44Z", "title": "https://test/", "text": "test"}'
            ]

        self.assertEqual(validate_passed_pages(passed_pages_missing_format), 0)

        passed_pages_missing_id = [
            '{"format": "json-pages-1.0", "title": "All Pages", "hasText": true}',
            '{"s://test/", "ts": "2020-12-07T14:34:44Z", "title": "https://test/", "text": "test"}'
            ]

        self.assertEqual(validate_passed_pages(passed_pages_missing_id), 0)

        passed_pages_missing_title = [
            '{"format": "json-pages-1.0", "id": "pages", "hasText": true}',
            '{"s://test/", "ts": "2020-12-07T14:34:44Z", "title": "https://test/", "text": "test"}'
            ]

        self.assertEqual(validate_passed_pages(passed_pages_missing_title), 0)


if __name__ == "__main__":
    unittest.main()
