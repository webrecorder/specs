import unittest, os, zipfile, sys, hashlib
from wacz.main import main

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")

class TestWaczFormat(unittest.TestCase):

    def support_hash_file(self, file):
        '''Hashes the passed file using md5'''
        BUF_SIZE = 65536
        md5 = hashlib.md5()
        with open(file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
        f.close()
        print(f)
        return md5.hexdigest()
    
    @classmethod
    def setUpClass(self):
        sys.stdout = open(os.devnull, 'w') # Suppress print statements in the setup for testing clarity 
        
        main(['-o', os.path.join(TEST_DIR, 'example.wacz'), os.path.join(TEST_DIR, 'example-collection.warc')])
        with zipfile.ZipFile(os.path.join(TEST_DIR, 'example.wacz'), "r") as zip_ref:
            zip_ref.extractall("tests/fixtures/unizpped_wacz")
            zip_ref.close()
        
        self.wacz_file = os.path.join(TEST_DIR, 'example.wacz')
        self.warc_file = os.path.join(TEST_DIR, 'example-collection.warc')
        self.wacz_archive = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unizpped_wacz/archive/example-collection.warc")
        self.wacz_index_cdx = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unizpped_wacz/indexes/index.cdx.gz")
        self.wacz_index_idx = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unizpped_wacz/indexes/index.idx")
        self.wacz_yaml = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unizpped_wacz/webarchive.yaml")
            
    def test_components(self):
        '''Check that the basic components of a wacz file exist'''
        self.assertEqual(os.path.exists(self.wacz_archive), True)
        self.assertEqual(os.path.exists(self.wacz_index_cdx), True)
        self.assertEqual(os.path.exists(self.wacz_index_idx), True)
        self.assertEqual(os.path.exists(self.wacz_yaml), True)

    def test_archive_structure(self):
        '''Check that the hash of the original warc file matches that of the warc file in the archive folder'''
        original_warc = self.support_hash_file(self.warc_file)
        unizpped_wacz = self.support_hash_file(self.wacz_archive)
        self.assertEqual(original_warc, unizpped_wacz)


if __name__ == '__main__':
    unittest.main()
