import unittest
import tempfile
import os
from wacz.main import main, now
import zipfile

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestWaczIndexing(unittest.TestCase):
    def test_warc_with_other_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-warcinfo-metadata.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-warcinfo-metadata.wacz"),
                    ]
                ),
                0,
            )

            self.assertEqual(
                main(
                    [
                        "validate",
                        "-f",
                        os.path.join(tmpdir, "example-warcinfo-metadata.wacz"),
                    ]
                ),
                0,
            )

    def test_warc_with_extra_lists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection-with-lists.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection-with-lists.wacz"),
                    ]
                ),
                0,
            )

            self.assertEqual(
                main(
                    [
                        "validate",
                        "-f",
                        os.path.join(tmpdir, "example-collection-with-lists.wacz"),
                    ]
                ),
                0,
            )

            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-with-lists.wacz")
            ) as zf:
                filelist = sorted(zf.namelist())

                # verify pages file added for each list
                self.assertEqual(
                    filelist,
                    [
                        "archive/example-collection-with-lists.warc",
                        "datapackage.json",
                        "indexes/index.cdx.gz",
                        "indexes/index.idx",
                        "pages/example.jsonl",
                        "pages/iana.jsonl",
                        "pages/pages.jsonl",
                    ],
                )
