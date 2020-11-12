import unittest, os, zipfile, sys, gzip, json
from wacz.main import main
from wacz.util import support_hash_file
from frictionless import validate
from wacz.validate import Validation

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestWaczFormat(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        with zipfile.ZipFile(
            os.path.join(TEST_DIR, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall("tests/fixtures/unzipped_wacz_1")
            zip_ref.close()

        with zipfile.ZipFile(
            os.path.join(TEST_DIR, "valid_example_2.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall("tests/fixtures/unzipped_wacz_2")
            zip_ref.close()

        self.validation_class_valid_2 = Validation(
            os.path.join(TEST_DIR, "valid_example_2.wacz")
        )
        self.validation_class_valid_1 = Validation(
            os.path.join(TEST_DIR, "valid_example_1.wacz")
        )
        self.validation_class_valid_0 = Validation(
            os.path.join(TEST_DIR, "valid_example_0.wacz")
        )
        self.validation_class_invalid = Validation(
            os.path.join(TEST_DIR, "invalid_example_1.wacz")
        )

    def test_overall_command(self):
        self.assertTrue(
            main(["validate", "-f", os.path.join(TEST_DIR, "valid_example_0.wacz")])
        )
        self.assertTrue(
            (["validate", "-f", os.path.join(TEST_DIR, "valid_example_1.wacz")])
        )
        self.assertTrue(
            (["validate", "-f", os.path.join(TEST_DIR, "valid_example_2.wacz")])
        )

    def test_check_indexes_valid(self):
        self.assertTrue(self.validation_class_valid_1.check_indexes())

    def test_check_compression_valid(self):
        self.assertTrue(self.validation_class_valid_1.check_compression())
        self.assertTrue(self.validation_class_valid_2.check_compression())

    def test_frictionless_validate_valid_wacz(self):
        """Check that the frictionless validation feature identifies a valid wacz data package as valid"""
        # Use frictionless validation
        valid_1 = self.validation_class_valid_1.frictionless_validate()
        self.assertTrue(valid_1)

        valid_2 = self.validation_class_valid_2.frictionless_validate()
        self.assertTrue(valid_2)

    def test_frictionless_validate_invalid_wacz(self):
        """Check that the frictionless validation feature identifies an invalid wacz data package as invalid"""
        # Use frictionless validation
        valid = self.validation_class_invalid.frictionless_validate()
        self.assertFalse(valid)

    def test_filepaths_invalid_wacz(self):
        """Correctly fail on a wacz with invalid files"""
        valid = self.validation_class_invalid.check_file_paths()
        self.assertFalse(valid)

    def test_filepaths_valid_wacz(self):
        """Correctly succeed on a wacz with valid files"""
        valid_1 = self.validation_class_valid_1.check_file_paths()
        self.assertTrue(valid_1)

        valid_2 = self.validation_class_valid_2.check_file_paths()
        self.assertTrue(valid_2)

    def test_hashes_valid_wacz(self):
        """Correctly succeed on a wacz with matching hashes"""
        valid_1 = self.validation_class_valid_1.check_file_hashes()
        self.assertTrue(valid_1)

        valid_2 = self.validation_class_valid_2.check_file_hashes()
        self.assertTrue(valid_2)

    def test_hashes_invalid_wacz(self):
        """Correctly fail on a wacz with nonmatching hashes"""
        valid = self.validation_class_invalid.check_file_hashes()
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
