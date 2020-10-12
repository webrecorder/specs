import unittest, os, zipfile, sys, hashlib, yaml, gzip
from wacz.main import main, now
from unittest.mock import patch

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
        return md5.hexdigest()
    
    @classmethod
    @patch('wacz.main.now')
    def setUpClass(self, mock_now):   
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        main(['-o', os.path.join(TEST_DIR, 'example.wacz'), os.path.join(TEST_DIR, 'example-collection.warc')])
        with zipfile.ZipFile(os.path.join(TEST_DIR, 'example.wacz'), "r") as zip_ref:
            zip_ref.extractall("tests/fixtures/unzipped_wacz")
            zip_ref.close()
        
        self.wacz_file = os.path.join(TEST_DIR, 'example.wacz')
        self.warc_file = os.path.join(TEST_DIR, 'example-collection.warc')
        self.wacz_archive = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unzipped_wacz/archive/example-collection.warc")
        self.wacz_index_cdx = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unzipped_wacz/indexes/index.cdx.gz")
        self.wacz_index_idx = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unzipped_wacz/indexes/index.idx")
        self.wacz_yaml = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/unzipped_wacz/webarchive.yaml")
            
    def test_components(self):
        '''Check that the basic components of a wacz file exist'''
        self.assertEqual(os.path.exists(self.wacz_archive), True)
        self.assertEqual(os.path.exists(self.wacz_index_cdx), True)
        self.assertEqual(os.path.exists(self.wacz_index_idx), True)
        self.assertEqual(os.path.exists(self.wacz_yaml), True)

    def test_archive_structure(self):
        '''Check that the hash of the original warc file matches that of the warc file in the archive folder'''
        original_warc = self.support_hash_file(self.warc_file)
        unzipped_wacz = self.support_hash_file(self.wacz_archive)
        self.assertEqual(original_warc, unzipped_wacz)
    
    def test_yaml_structure(self):
        '''Check that the wacz yaml file has the expected values'''
        with open(self.wacz_yaml, 'rb') as f:
            yaml_dict = (yaml.load(f, Loader=yaml.FullLoader))
            pages_dict = yaml_dict['pages'][0]
        f.close()

        self.assertEqual('pages' in yaml_dict.keys(), True)
        self.assertEqual('title' in yaml_dict.keys(), True)
        self.assertEqual(yaml_dict['title'], 'Example Collection')

        self.assertEqual('date' in pages_dict.keys(), True)
        self.assertEqual('title' in pages_dict.keys(), True)
        self.assertEqual('url' in pages_dict.keys(), True)
        self.assertEqual(pages_dict['title'], 'Example Domain')
        self.assertEqual(pages_dict['url'], 'http://www.example.com/')
        self.assertEqual(pages_dict['date'], '2020-10-07T21:22:36Z')

    def test_idx_structure(self):
        '''Check that the idx file has the expected content'''
        with open(self.wacz_index_idx, 'rb') as f:
            content = f.read()
        f.close()
        self.assertEqual(content, b'!meta 0 {"format": "cdxj-gzip-1.0", "filename": "index.cdx.gz"}\ncom,example)/ 20201007212236 {"offset": 0, "length": 194}\n')

    def test_cdx_structure(self):
        '''Check that the cdx file has the expected content'''
        content = ''
        with gzip.open(self.wacz_index_cdx, 'rb') as f:
            for line in f:
                content = content + line.decode()
        f.close()
        self.assertEqual(content, 'com,example)/ 20201007212236 {"url": "http://www.example.com/", "mime": "text/html", "status": "200", "digest": "WJM2KPM4GF3QK2BISVUH2ASX64NOUY7L", "length": "1293", "offset": "845", "filename": "example-collection.warc"}\n')
        

if __name__ == '__main__':
    unittest.main()
