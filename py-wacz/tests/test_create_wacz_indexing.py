import unittest
import tempfile
import os
from wacz.main import main, now

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestWaczIndexing(unittest.TestCase):
    def test_warc_with_other_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-warcinfo-metadata.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-warcinfo-metadata.wacz"),
                    ]
                )
            )

            self.assertTrue(
                main(
                    [
                        "validate",
                        "-f",
                        os.path.join(tmpdir, "example-warcinfo-metadata.wacz"),
                    ]
                )
            )
