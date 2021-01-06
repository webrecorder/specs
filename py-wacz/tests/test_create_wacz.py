import unittest, os, zipfile, sys, gzip, json, tempfile
from wacz.main import main, now
from unittest.mock import patch
from wacz.util import support_hash_file
from frictionless import validate, Report

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestWaczFormat(unittest.TestCase):
    def find_resource(self, resource_list, filename):
        for file in resource_list:
            if filename in file["path"]:
                return file

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

        self.wacz_file = os.path.join(self.tmpdir.name, "valid_example_1.wacz")
        self.warc_file = os.path.join(TEST_DIR, "example-collection.warc")

        self.wacz_archive = os.path.join(
            self.tmpdir.name,
            "unzipped_wacz_1/archive/example-collection.warc",
        )
        self.wacz_index_cdx = os.path.join(
            self.tmpdir.name,
            "unzipped_wacz_1/indexes/index.cdx.gz",
        )
        self.wacz_index_idx = os.path.join(
            self.tmpdir.name,
            "unzipped_wacz_1/indexes/index.idx",
        )
        self.wacz_json = os.path.join(
            self.tmpdir.name,
            "unzipped_wacz_1/datapackage.json",
        )

    def test_components(self):
        """Check that the basic components of a wacz file exist"""
        self.assertTrue(
            "example-collection.warc"
            in os.listdir(os.path.join(self.tmpdir.name, "unzipped_wacz_1/archive"))
        )
        self.assertTrue(
            "index.cdx.gz"
            in os.listdir(os.path.join(self.tmpdir.name, "unzipped_wacz_1/indexes"))
        )
        self.assertTrue(
            "index.idx"
            in os.listdir(os.path.join(self.tmpdir.name, "unzipped_wacz_1/indexes"))
        )
        self.assertTrue(
            "pages.jsonl"
            in os.listdir(os.path.join(self.tmpdir.name, "unzipped_wacz_1/pages"))
        )
        self.assertTrue(
            "datapackage.json"
            in os.listdir(os.path.join(self.tmpdir.name, "unzipped_wacz_1/"))
        )

    def test_archive_structure(self):
        """Check that the hash of the original warc file matches that of the warc file in the archive folder"""
        f = open(self.warc_file, "rb")
        original_warc = support_hash_file("sha256", f.read())
        f.close()

        f = open(self.wacz_archive, "rb")
        archive_warc = support_hash_file("sha256", f.read())
        f.close()

        self.assertEqual(original_warc, archive_warc)

    def test_idx_structure(self):
        """Check that the idx file has the expected content"""
        with open(self.wacz_index_idx, "rb") as f:
            content = f.read()
        f.close()
        self.assertEqual(
            content,
            b'!meta 0 {"format": "cdxj-gzip-1.0", "filename": "index.cdx.gz"}\ncom,example)/ 20201007212236 {"offset": 0, "length": 194}\n',
        )

    def test_cdx_structure(self):
        """Check that the cdx file has the expected content"""
        content = ""
        with gzip.open(self.wacz_index_cdx, "rb") as f:
            for line in f:
                content = content + line.decode()
        f.close()
        self.assertEqual(
            content,
            'com,example)/ 20201007212236 {"url": "http://www.example.com/", "mime": "text/html", "status": "200", "digest": "WJM2KPM4GF3QK2BISVUH2ASX64NOUY7L", "length": "1293", "offset": "845", "filename": "example-collection.warc"}\n',
        )

    def test_data_package_structure(self):
        """Check that the package_descriptor is valid"""
        f = open(self.wacz_json, "rb")
        json_parse = json.loads(f.read())
        # Make sure it's recording the correct number of resources
        self.assertEqual(len(json_parse["resources"]), 4)

        # Check that the correct hash was recorded for a warc
        f = open(self.warc_file, "rb")
        original_warc = support_hash_file("sha256", f.read())
        f.close()

        warc_resource = self.find_resource(
            json_parse["resources"], "example-collection.warc"
        )
        self.assertEqual(original_warc, warc_resource["stats"]["hash"])

        # Check that the correct hash was recorded for the index.idx
        f = open(self.wacz_index_idx, "rb")
        original_wacz_index_idx = support_hash_file("sha256", f.read())
        f.close()
        idx_resource = self.find_resource(json_parse["resources"], "idx")
        self.assertEqual(original_wacz_index_idx, idx_resource["stats"]["hash"])

        # Check that the correct hash was recorded for the index.cdx.gz
        f = open(self.wacz_index_cdx, "rb")
        original_wacz_index_cdx = support_hash_file("sha256", f.read())
        f.close()
        cdx_resource = self.find_resource(json_parse["resources"], "cdx")
        self.assertEqual(original_wacz_index_cdx, cdx_resource["stats"]["hash"])

        # Use frictionless validation
        valid = validate(self.wacz_json)
        self.assertTrue(valid.valid)


if __name__ == "__main__":
    unittest.main()
