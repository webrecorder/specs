import unittest, os, zipfile, sys, gzip, json, tempfile
from wacz.main import main
from frictionless import validate
from wacz.validate import Validation
from unittest.mock import patch

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestWaczFormat(unittest.TestCase):
    @classmethod
    @patch("wacz.main.now")
    def setUpClass(self, mock_now):
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        self.tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(self.tmpdir.name, "valid_example_1.wacz"),
            ]
        )
        with zipfile.ZipFile(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(self.tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        self.validation_class_valid_1 = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )
        self.validation_class_invalid = Validation(
            os.path.join(TEST_DIR, "invalid_example_1.wacz")
        )

    def test_overall_command(self):
        self.assertTrue(
            (["validate", "-f", os.path.join(self.tmpdir.name, "valid_example_1.wacz")])
        )

    def test_check_indexes_valid(self):
        self.assertTrue(self.validation_class_valid_1.check_indexes())

    def test_check_compression_valid(self):
        self.assertTrue(self.validation_class_valid_1.check_compression())

    def test_frictionless_validate_valid_wacz(self):
        """Check that the frictionless validation feature identifies a valid wacz data package as valid"""
        # Use frictionless validation
        valid_1 = self.validation_class_valid_1.frictionless_validate()
        self.assertTrue(valid_1)

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

    def test_hashes_valid_wacz(self):
        """Correctly succeed on a wacz with matching hashes"""
        valid_1 = self.validation_class_valid_1.check_file_hashes()
        self.assertTrue(valid_1)

    def test_hashes_invalid_wacz(self):
        """Correctly fail on a wacz with nonmatching hashes"""
        valid = self.validation_class_invalid.check_file_hashes()
        self.assertFalse(valid)

    def test_ability_to_detect_hash_md5(self):
        """Correctly identify the hash type of a file as md5"""
        tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(tmpdir.name, "valid_example_1.wacz"),
                "--hash-type",
                "md5",
            ]
        )
        with zipfile.ZipFile(
            os.path.join(tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        validation_class = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )
        valid = validation_class.detect_hash_type()
        self.assertEqual(valid, 0)
        valid = validation_class.hash_type
        self.assertEqual(valid, "md5")

    def test_ability_to_detect_hash_md5(self):
        """Correctly validate hashes and identify the type when no flag is set to md5"""
        tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(tmpdir.name, "valid_example_1.wacz"),
                "--hash-type",
                "sha256",
            ]
        )
        with zipfile.ZipFile(
            os.path.join(tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        validation_class = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )
        valid = validation_class.detect_hash_type()
        self.assertEqual(valid, 0)
        valid = validation_class.hash_type
        self.assertEqual(valid, "sha256")

    def test_ability_to_detect_hash_md5(self):
        """Correctly validate hashes and identify the type when flag is set to 256"""
        tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(tmpdir.name, "valid_example_1.wacz"),
                "--hash-type",
                "sha256",
            ]
        )
        with zipfile.ZipFile(
            os.path.join(tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        validation_class = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )
        valid = validation_class.detect_hash_type()
        self.assertEqual(valid, 0)
        valid = validation_class.hash_type
        self.assertEqual(valid, "sha256")

    def test_invalid_wacz_missing_datapackage(self):
        """Correctly validate hashes and identify the type when no flag is set"""
        tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(tmpdir.name, "valid_example_1.wacz"),
            ]
        )
        with zipfile.ZipFile(
            os.path.join(tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        os.remove(os.path.join(tmpdir.name, "unzipped_wacz_1/datapackage.json"))
        validation_class = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )

        valid = validation_class.check_required_contents()
        self.assertEqual(valid, 0)

    def test_invalid_wacz_missing_index(self):
        """Correctly fail on a wacz with no index"""
        tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(tmpdir.name, "valid_example_1.wacz"),
            ]
        )
        with zipfile.ZipFile(
            os.path.join(tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        os.remove(os.path.join(tmpdir.name, "unzipped_wacz_1/indexes/index.cdx.gz"))
        validation_class = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )
        valid = validation_class.check_required_contents()
        self.assertEqual(valid, 0)

    def test_invalid_wacz_missing_warc(self):
        """Correctly fail on a wacz with no warc file"""
        tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(tmpdir.name, "valid_example_1.wacz"),
            ]
        )
        with zipfile.ZipFile(
            os.path.join(tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        os.remove(
            os.path.join(tmpdir.name, "unzipped_wacz_1/archive/example-collection.warc")
        )
        validation_class = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )
        valid = validation_class.check_required_contents()
        self.assertEqual(valid, 0)

    def test_invalid_wacz_missing_pages(self):
        """Correctly fail on a wacz with no pages file"""
        tmpdir = tempfile.TemporaryDirectory()
        main(
            [
                "create",
                "-f",
                os.path.join(TEST_DIR, "example-collection.warc"),
                "-o",
                os.path.join(tmpdir.name, "valid_example_1.wacz"),
            ]
        )
        with zipfile.ZipFile(
            os.path.join(tmpdir.name, "valid_example_1.wacz"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(tmpdir.name, "unzipped_wacz_1"))
            zip_ref.close()

        os.remove(os.path.join(tmpdir.name, "unzipped_wacz_1/pages/pages.jsonl"))
        validation_class = Validation(
            os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        )
        valid = validation_class.check_required_contents()
        self.assertEqual(valid, 0)


if __name__ == "__main__":
    unittest.main()
