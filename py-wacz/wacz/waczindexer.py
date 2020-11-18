import json, shortuuid
from urllib.parse import quote, urlsplit, urlunsplit
import os, gzip, glob
from cdxj_indexer.main import CDXJIndexer
from warcio.timeutils import iso_date_to_timestamp, timestamp_to_iso_date
from boilerpy3 import extractors
from wacz.util import support_hash_file

HTML_MIME_TYPES = ("text/html", "application/xhtml", "application/xhtml+xml")

PAGE_INDEX = "pages/pages.jsonl"


# ============================================================================
class WACZIndexer(CDXJIndexer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = {}
        self.lists = {}
        self.title = ""
        self.desc = ""
        self.main_url = kwargs.pop("main_url", "")
        self.main_ts = kwargs.pop("main_ts", "")

        if self.main_ts != None and self.main_ts != "":
            self.main_ts_flag = False

        if self.main_url != None and self.main_url != "":
            self.main_url_flag = False
        # if url is missing path segment, ensure it is set to '/'
        try:
            parts = list(urlsplit(self.main_url))
            if not parts[2]:
                parts[2] = "/"
                self.main_url = urlunsplit(parts)
        except:
            pass

        self.detect_pages = kwargs.get("detect_pages")
        self.referrers = set()

    def process_index_entry(self, it, record, *args):
        type_ = record.rec_headers.get("WARC-Type")
        if type_ == "warcinfo":
            self.parse_warcinfo(record)

        elif type_ in CDXJIndexer.DEFAULT_RECORDS:
            if type_ in ("response" "resource"):
                self.extract_text(record)

            super().process_index_entry(it, record, *args)

    def process_all(self):
        super().process_all()

        if self.detect_pages:
            to_delete = [
                id_
                for id_, value in self.pages.items()
                if value["url"] not in self.referrers
            ]
            for delete in to_delete:
                del self.pages[delete]

            print("Num Pages Detected: {0}".format(len(self.pages)))

        if (
            hasattr(self, "main_url_flag")
            and hasattr(self, "main_ts_flag")
            and self.main_url_flag == False
            and self.main_ts_flag == False
        ):
            raise ValueError(
                "ts %s not found in index with %s" % (self.main_ts, self.main_url)
            )

        if hasattr(self, "main_url_flag") and self.main_url_flag == False:
            raise ValueError("Url %s not found in index" % (self.main_url))

    def _do_write(self, urlkey, ts, index, out):
        if self.detect_pages:
            self.detect_page(ts, index)

        super()._do_write(urlkey, ts, index, out)

    def detect_page(self, ts, index):
        referrer = index.get("referrer")
        if referrer:
            self.referrers.add(referrer)

    def _read_record(self, record):
        if hasattr(record, "buffered_stream"):
            content = record.buffered_stream.read()
        else:
            content = record.content_stream().read()

        return content

    def parse_warcinfo(self, record):
        """Parse WARC information.
        :param record: WARC information
        :returns: WARC information or None
        :rtype: dict or None
        """
        warcinfo = {}
        warcinfo_buff = self._read_record(record)
        warcinfo_buff = warcinfo_buff.decode("utf-8")
        metadata = None
        for line in warcinfo_buff.rstrip().split("\n"):
            parts = line.split(":", 1)
            if parts[0] == "json-metadata":
                metadata = json.loads(parts[1])
            elif len(parts) == 2:
                warcinfo[parts[0]] = parts[1].strip()

        if not metadata or "type" not in metadata:
            return

        if metadata["type"] == "collection":
            self.title = metadata.get("title", "")
            self.desc = metadata.get("desc", "")

        elif metadata["type"] == "recording":
            pages = metadata.get("pages", [])
            for page in pages:
                id_ = page["timestamp"] + "/" + page["url"]
                self.pages[id_] = page

        self.detect_pages = False

    def extract_text(self, record):
        url = record.rec_headers.get("WARC-Target-URI")
        date = record.rec_headers.get("WARC-Date")
        ts = iso_date_to_timestamp(date)
        id_ = ts + "/" + url

        if (
            self.main_url
            and self.main_url == url
            and self.main_ts
            and self.main_ts == ts
        ):
            self.main_ts_flag = True
            self.main_url_flag = True
            print("Found Main Url: {0}".format(url))
            print("Found Main ts: {0}".format(ts))
            self.pages[id_] = {"timestamp": ts, "url": url, "title": url}
        if self.main_url and self.main_url == url and self.main_ts == None:
            self.main_url_flag = True
            print("Found Main Url: {0}".format(url))
            self.pages[id_] = {"timestamp": ts, "url": url, "title": url}

        mime = self.get_record_mime_type(record)

        if mime not in HTML_MIME_TYPES:
            return

        status = record.http_headers.get_statuscode()
        if record.http_headers and status.startswith("3"):
            return

        if id_ not in self.pages:
            if self.detect_pages:
                self.pages[id_] = {"timestamp": ts, "url": url, "title": url}
            else:
                return

        content = self._read_record(record)
        if not content:
            return

        try:
            extractor = extractors.ArticleExtractor()

            content = content.decode("utf-8")

            doc = extractor.get_doc(content)

            if doc.content:
                self.pages[id_]["text"] = doc.content

            if doc.title:
                self.pages[id_]["title"] = doc.title

        except Exception as e:
            print(e)
            # skip text extraction in case of errors
            pass

    def get_record_mime_type(self, record):
        if record.http_headers:
            # if the record has HTTP headers, use the Content-Type from those (eg. 'response' record)
            content_type = record.http_headers["Content-Type"]
        else:
            # otherwise, use the Content-Type from WARC headers
            content_type = record.rec_headers["Content-Type"]

        mime = content_type or ""
        return mime.split(";")[0]

    def serialize_cdxj_pages(self, pages):
        yield "!meta 0 " + json.dumps(
            {"format": "cdxj-pages-1.0", "title": "All Pages"}
        )

        for line in pages.values():
            ts = timestamp_to_iso_date(line["timestamp"])
            title = quote(line.get("title") or line.get("url"), safe=":/?&=")

            data = {"url": line["url"]}
            if "text" in line:
                data["text"] = line["text"]

            yield title + " " + ts + " " + json.dumps(data)

    def serialize_json_pages(self, pages):
        yield json.dumps({"format": "json-pages-1.0", "title": "All Pages"}) + "\n"
        id = shortuuid.uuid()
        for line in pages.values():
            ts = timestamp_to_iso_date(line["timestamp"])
            title = line.get("title")

            data = {"id": id, "url": line["url"], "ts": ts}
            if title:
                data["title"] = title

            if "text" in line:
                data["text"] = line["text"]

            yield json.dumps(data) + "\n"

    def generate_metadata(self, res, wacz):

        package_dict = {}
        package_dict["profile"] = "data-package"
        package_dict["resources"] = []
        for i in range(0, len(wacz.infolist())):
            file = wacz.infolist()[i]
            package_dict["resources"].append({})
            package_dict["resources"][i]["path"] = file.filename
            with wacz.open(file, "r") as myfile:
                content = myfile.read()
                package_dict["resources"][i]["stats"] = {}
                package_dict["resources"][i]["stats"]["hash"] = support_hash_file(
                    content
                )
                package_dict["resources"][i]["stats"]["bytes"] = len(content)
                package_dict["resources"][i]["hashing"] = "sha256"

        desc = res.desc or self.desc
        title = res.title or self.title

        data = {}
        if title:
            package_dict["title"] = title

        if desc:
            package_dict["desc"] = desc

        if self.main_url:
            package_dict["mainPageURL"] = self.main_url
            if self.main_ts:
                package_dict["mainPageTS"] = self.main_ts

        if res.date:
            package_dict["mainPageTS"] = res.date
        return json.dumps(package_dict, indent=2)
