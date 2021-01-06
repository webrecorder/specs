import unittest, hashlib, datetime
from wacz.util import support_hash_file


class TestUtil(unittest.TestCase):
    def test_support_hash_file(self):
        """Check that the hash function works correctly"""

        test_string = "test"
        self.assertEqual(
            hashlib.sha256(test_string).hexdigest(),
            support_hash_file("sha256", test_string),
        )
        self.assertEqual(
            hashlib.sha256(test_string).hexdigest(),
            support_hash_file("md5", test_string),
        )


if __name__ == "__main__":
    unittest.main()
