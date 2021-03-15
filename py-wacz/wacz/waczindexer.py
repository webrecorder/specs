import json, shortuuid
from urllib.parse import quote, urlsplit, urlunsplit
import os, gzip, glob, zipfile
from cdxj_indexer.main import CDXJIndexer
from warcio.timeutils import iso_date_to_timestamp, timestamp_to_iso_date
from boilerpy3 import extractors
from wacz.util import support_hash_file, now, WACZ_VERSION

HTML_MIME_TYPES = ("text/html", "application/xhtml", "application/xhtml+xml")

# Add warcinfo as a default record for indexing to simplify filtering logic
CDXJIndexer.DEFAULT_RECORDS.append("warcinfo")


# ============================================================================
class WACZIndexer(CDXJIndexer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = {}
        self.extra_page_lists = {}
        self.title = ""
        self.desc = ""
        self.has_text = False
        self.main_url = kwargs.pop("main_url", "")
        self.main_ts = kwargs.pop("main_ts", "")
        self.hash_type = kwargs.pop("hash_type", "")

        # If the user has specified a hash type use that otherwise default to sha256
        if self.hash_type == None:
            self.hash_type = "sha256"

        self.passed_pages_dict = kwargs.pop("passed_pages_dict", "")

        if self.main_url != None and self.main_url != "":
            self.main_url_flag = False
            self.main_ts_flag = False
        # if url is missing path segment, ensure it is set to '/'
        try:
            parts = list(urlsplit(self.main_url))
            if not parts[2]:
                parts[2] = "/"
                self.main_url = urlunsplit(parts)
        except:
            pass

        self.detect_pages = kwargs.get("detect_pages")
        self.extract_text = kwargs.get("extract_text")
        if self.extract_text == True and self.detect_pages == False:
            print(
                "Warning. You've passed the --text flag without the --detect-pages flag. No pages.jsonl file will be generated. You must enable the --detect-pages and --text flags together in order to get a pages.jsonl file with full text."
            )
        self.referrers = set()

    def process_index_entry(self, it, record, *args):
        type_ = record.rec_type
        if type_ == "warcinfo":
            self.parse_warcinfo(record)

        elif self.filter_record(record):
            if type_ in ("response" "resource"):
                self.check_pages_and_text(record)

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

            if self.passed_pages_dict == {}:
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
            lists = metadata.get("lists")
            if lists:
                self.extract_page_lists(lists)

        # Don't add the record to the self.pages if were evaluating passed in pages
        elif metadata["type"] == "recording" and self.passed_pages_dict == {}:
            pages = metadata.get("pages", [])
            for page in pages:
                id_ = page["timestamp"] + "/" + page["url"]
                self.pages[id_] = page

        self.detect_pages = False

    def extract_page_lists(self, lists):
        for pagelist in lists:
            pagelist_header = {}
            # unique id for this page list, will also be the filename
            if "slug" in pagelist:
                uid = pagelist["slug"]
            else:
                uid = shortuuid.uuid()

            text_list = list(
                self.serialize_json_pages(
                    pages=pagelist["bookmarks"],
                    id=uid,
                    title=pagelist.get("title"),
                    desc=pagelist.get("desc"),
                )
            )

            self.extra_page_lists[uid] = text_list

    def check_pages_and_text(self, record):
        url = record.rec_headers.get("WARC-Target-URI")
        date = record.rec_headers.get("WARC-Date")
        ts = iso_date_to_timestamp(date)
        id_ = ts + "/" + url
        matched_id = ""
        # Check for both a matching url/ts and url entry
        if id_ in self.passed_pages_dict:
            matched_id = id_
        if url in self.passed_pages_dict:
            matched_id = url
        # If we find a match build a record
        if matched_id != "":
            self.pages[matched_id] = {"timestamp": ts, "url": url, "title": url}
            # Add title and text if they've been provided
            if "title" in self.passed_pages_dict[matched_id]:
                self.pages[matched_id]["title"] = self.passed_pages_dict[matched_id][
                    "title"
                ]
            if "text" in self.passed_pages_dict[matched_id]:
                self.pages[matched_id]["text"] = self.passed_pages_dict[matched_id][
                    "text"
                ]
            # Delete the entry from our pages_dict so we can't match it again
            del self.passed_pages_dict[matched_id]

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
            # If were not relying on passed in pages we want to add all records to the self.pages object
            if self.passed_pages_dict == {}:
                self.pages[id_] = {"timestamp": ts, "url": url, "title": url}
        if self.main_url and self.main_url == url and self.main_ts == None:
            self.main_url_flag = True
            print("Found Main Url: {0}".format(url))
            if id_ not in self.pages:
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

        # if not extracting text, then finish here
        if not self.extract_text:
            return

        content = self._read_record(record)
        if not content:
            return

        try:
            extractor = extractors.ArticleExtractor()

            content = content.decode("utf-8")

            doc = extractor.get_doc(content)

            curr_page = self.pages[id_]

            if doc.content:
                self.pages[id_]["text"] = doc.content
                self.has_text = True

            # only set title if unset, or set to url (default)
            # avoid overriding user-specified title, if any
            if doc.title and self.pages[id_].get("title", url) == url:
                self.pages[id_]["title"] = doc.title

        except Exception as e:
            # skip text extraction in case of errors
            print("Skipping, Text Extraction Failed For: " + url)
            print(e)

    def get_record_mime_type(self, record):
        if record.http_headers:
            # if the record has HTTP headers, use the Content-Type from those (eg. 'response' record)
            content_type = record.http_headers["Content-Type"]
        else:
            # otherwise, use the Content-Type from WARC headers
            content_type = record.rec_headers["Content-Type"]

        mime = content_type or ""
        return mime.split(";")[0]

    def write_page_list(self, wacz, filename, page_iter):
        pages_file = zipfile.ZipInfo(filename, now())
        pages_file.compress_type = zipfile.ZIP_DEFLATED

        with wacz.open(pages_file, "w") as pg_fh:
            for line in page_iter:
                pg_fh.write(line.encode("utf-8"))

    def serialize_json_pages(self, pages, id, title, desc=None, has_text=False):
        page_header = {"format": "json-pages-1.0", "id": id}

        if title:
            page_header["title"] = title

        if desc:
            page_header["description"] = desc

        if has_text:
            page_header["hasText"] = True

        yield json.dumps(page_header) + "\n"

        for line in pages:
            ts = timestamp_to_iso_date(line["timestamp"])
            page_title = line.get("title")

            uid = line.get("id") or line.get("page_id") or shortuuid.uuid()

            data = {"id": uid, "url": line["url"], "ts": ts}

            if page_title:
                data["title"] = page_title

            if "text" in line:
                data["text"] = line["text"]

            yield json.dumps(data) + "\n"

    def generate_metadata(self, res, wacz):
        package_dict = {}
        metadata = {}

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
                    self.hash_type, content
                )
                package_dict["resources"][i]["stats"]["bytes"] = len(content)
                package_dict["resources"][i]["hashing"] = self.hash_type

        # set optional metadata
        desc = res.desc or self.desc
        title = res.title or self.title

        if title:
            metadata["title"] = title

        if desc:
            metadata["desc"] = desc

        if self.main_url:
            metadata["mainPageURL"] = self.main_url
            if self.main_ts:
                metadata["mainPageTS"] = self.main_ts

        if res.date:
            metadata["mainPageTS"] = res.date

        package_dict["metadata"] = metadata
        package_dict["wacz_version"] = WACZ_VERSION

        return json.dumps(package_dict, indent=2)
