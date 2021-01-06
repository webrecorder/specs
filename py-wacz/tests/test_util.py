import unittest
import tempfile
import os
import zipfile, json, gzip, hashlib
from wacz.util import support_hash_file, validateJSON

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestUtilFunctions(unittest.TestCase):
    def test_util_hash(self):
        """When invoking the util hash method a  hash should be returned"""
        test_hash = hashlib.sha256("test".encode("utf-8")).hexdigest()
        self.assertEqual(support_hash_file("sha256", "test".encode("utf-8")), test_hash)

        test_hash = hashlib.md5("test".encode("utf-8")).hexdigest()
        self.assertEqual(support_hash_file("md5", "test".encode("utf-8")), test_hash)

    def test_util_validate_json_succeed(self):
        """validate json method should succed with valid json"""
        self.assertTrue(validateJSON('{"test": "test"}'))

    def test_util_validate_json_fail(self):
        """validate json method should fail with valid json"""
        self.assertFalse(validateJSON('test": "test"}'))


if __name__ == "__main__":
    unittest.main()
