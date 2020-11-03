import tempfile, os, zipfile, json, pathlib, pkg_resources
from frictionless import validate
from wacz.util import support_hash_file

class Validation(object):
    def __init__(self, file):
        self.dir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(self.dir.name)
            zip_ref.close()
        self.version = self.detect_version()

    def detect_version(self):
        self.version = None
        if os.path.exists(os.path.join(self.dir.name, 'datapackage.json')):
            self.version = pkg_resources.get_distribution('wacz').version
            print("\nVersion detected as %s" % self.version)
            self.data_folder = os.listdir(self.dir.name)
            self.datapackage_path = os.path.join(self.dir.name, 'datapackage.json')
            self.datapackage = json.loads(open(self.datapackage_path, 'rb').read())
        elif os.path.exists(os.path.join(self.dir.name, 'webarchive.yaml')):
            self.version = '0.0'
            self.webarchive_yaml = os.path.join(self.dir.name, 'webarchive.yaml')
            print("\nVersion detected as 0.0")
        else:
            print("\nVersion not able to be detected, invalid wacz file")
        return self.version
        
    def frictionless_validate(self):
        '''Uses the frictionless data package to validate the datapackage.json file'''
        if validate(self.datapackage_path).valid == True:
            return True
        else:
            print("\nFrictionless has detected that this is an invalid package with errors %s" % validate(self.datapackage_path).errors)
            return False

    def check_file_paths(self):
        '''Uses the datapackage to check that all the files listed exist in the data folder or that the wacz contains a webarchive.yml file'''        
        if self.version != '0.0':
            package_files = ([ item['path'] for item in self.datapackage['resources']])
            for filepath in pathlib.Path(self.dir.name).glob('**/*.*'):
                if not os.path.basename(filepath).endswith('datapackage.json'):
                    file = str(filepath).split("/")[-2:]
                    file = ("/".join(file))
                    if file not in package_files:
                        print('file %s is not listed in the datapackage' % file)
                        return False
        return True
    
    def check_compression(self):
        '''WARCs and compressed cdx.gz should be in ZIP with 'store' compression (not deflate) Indexes and page list can be compressed'''        
        for filepath in pathlib.Path(self.dir.name).glob('**/*.*'):
            if os.path.basename(filepath).endswith('cdx.gz'):
                print(filepath)
                #zf = zipfile.ZipFile(filepath, 'r')
                #print(zf.compress_type)  
                print("END")
        
    def check_file_hashes(self):
        '''Uses the datapackage to check that all the hashes of file in the data folder match those in the datapackage'''
        for filepath in pathlib.Path(self.dir.name).glob('**/*.*'):
            if not os.path.basename(filepath).endswith('datapackage.json'):
                file = open(filepath, 'rb').read()
                hash = support_hash_file(file)
                file = str(filepath).split("/")[-2:]
                file = ("/".join(file))
                res = None
                for item in self.datapackage['resources']:
                     if item["path"] == file:
                         res = item
                if res == None or (res['stats']['hash'] != hash):
                    print("\nfile %s's hash does not match the has listed in the datapackage" % file)
                    return False
        return True

