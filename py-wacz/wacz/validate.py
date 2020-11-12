import tempfile, os, zipfile, json, pathlib, pkg_resources, gzip
from frictionless import validate
from wacz.util import support_hash_file, now
from wacz.waczindexer import WACZIndexer
from io import BytesIO, StringIO, TextIOWrapper

OUTDATED_WACZ = "0.1.0"


class Validation(object):
    def __init__(self, file):
        self.dir = tempfile.TemporaryDirectory()
        self.wacz = file
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(self.dir.name)
            zip_ref.close()
        self.version = self.detect_version()

    def detect_version(self):
        self.version = None
        if os.path.exists(os.path.join(self.dir.name, "datapackage.json")):
            self.version = pkg_resources.get_distribution("wacz").version
            print("\nVersion detected as %s" % self.version)
            self.data_folder = os.listdir(self.dir.name)
            self.datapackage_path = os.path.join(self.dir.name, "datapackage.json")
            self.datapackage = json.loads(open(self.datapackage_path, "rb").read())
        elif os.path.exists(os.path.join(self.dir.name, "webarchive.yaml")):
            self.version = OUTDATED_WACZ
            self.webarchive_yaml = os.path.join(self.dir.name, "webarchive.yaml")
            print(
                "\nWACZ version detected as 0.1.0. This is an outdated version of WACZ."
            )
        else:
            print("\nVersion not able to be detected, invalid wacz file")
        return self.version

    def frictionless_validate(self):
        """Uses the frictionless data package to validate the datapackage.json file"""
        if validate(self.datapackage_path).valid == True:
            return True
        else:
            print(
                "\nFrictionless has detected that this is an invalid package with errors %s"
                % validate(self.datapackage_path).errors
            )
            return False

    def check_file_paths(self):
        """Uses the datapackage to check that all the files listed exist in the data folder or that the wacz contains a webarchive.yml file"""
        if self.version != OUTDATED_WACZ:
            package_files = [item["path"] for item in self.datapackage["resources"]]
            for filepath in pathlib.Path(self.dir.name).glob("**/*.*"):
                if not os.path.basename(filepath).endswith("datapackage.json"):
                    file = str(filepath).split("/")[-2:]
                    file = "/".join(file)
                    if file not in package_files:
                        print("file %s is not listed in the datapackage" % file)
                        return False
        return True

    def check_compression(self):
        """WARCs and compressed cdx.gz should be in ZIP with 'store' compression (not deflate) Indexes and page list can be compressed"""
        wacz = zipfile.ZipInfo(self.wacz)
        if wacz.compress_type != 0:
            return False

        if os.path.exists(os.path.join(self.dir.name, "indexes/index.cdx.gz")):
            cdx = zipfile.ZipInfo(os.path.join(self.dir.name, "indexes/index.cdx.gz"))
            if cdx.compress_type != 0:
                return False

        archive_folder = os.listdir(os.path.join(self.dir.name, "archive"))
        for item in archive_folder:
            if ".warc" not in item and zf.getinfo(item).compress_type != 0:
                return False
        return True

    def check_indexes(self):
        """Indexing existing WARC which should match the index in the wacz"""
        if os.path.exists(os.path.join(self.dir.name, "indexes/index.cdx.gz")):
            for resource in self.datapackage["resources"]:
                if resource["path"] == "indexes/index.cdx.gz":
                    cdx = resource["stats"]["hash"]
        else:
            return False

        archive_folder = os.listdir(os.path.join(self.dir.name, "archive"))
        for item in archive_folder:
            if ".warc" in item:
                warc = item
        wacz_file = tempfile.NamedTemporaryFile(delete=False)
        wacz = zipfile.ZipFile(wacz_file.name, "w")
        data_file = zipfile.ZipInfo("indexes/index.cdx.gz", now())
        index_buff = BytesIO()
        text_wrap = TextIOWrapper(index_buff, "utf-8", write_through=True)
        wacz_indexer = None
        with wacz.open(data_file, "w") as data:
            wacz_indexer = WACZIndexer(
                text_wrap,
                {},
                sort=True,
                compress=data,
                fields="referrer",
                data_out_name="index.cdx.gz",
                records="all",
                main_url="",
                detect_pages="",
            )

            wacz_indexer.process_all()
        wacz.close()
        dir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(self.wacz, "r") as zip_ref:
            zip_ref.extractall(dir.name)
            zip_ref.close()

        with open(os.path.join(dir.name, "indexes/index.cdx.gz"), "rb") as fd:
            hash = support_hash_file(fd.read())
            gzip_fd = gzip.GzipFile(fileobj=fd)

        return cdx == hash

    def check_file_hashes(self):
        """Uses the datapackage to check that all the hashes of file in the data folder match those in the datapackage"""
        for filepath in pathlib.Path(self.dir.name).glob("**/*.*"):
            if not os.path.basename(filepath).endswith("datapackage.json"):
                file = open(filepath, "rb").read()
                hash = support_hash_file(file)
                file = str(filepath).split("/")[-2:]
                file = "/".join(file)
                res = None
                for item in self.datapackage["resources"]:
                    if item["path"] == file:
                        res = item
                if res == None or (res["stats"]["hash"] != hash):
                    print(
                        "\nfile %s's hash does not match the has listed in the datapackage"
                        % file
                    )
                    return False
        return True
