import json
from urllib.parse import quote, urlsplit, urlunsplit

import yaml
from cdxj_indexer.main import CDXJIndexer
from warcio.timeutils import iso_date_to_timestamp, timestamp_to_iso_date
from boilerpy3 import extractors


HTML_MIME_TYPES = ("text/html", "application/xhtml", "application/xhtml+xml")

PAGE_INDEX = "text/pages.pdx"


# ============================================================================
class WACZIndexer(CDXJIndexer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = {}
        self.lists = {}
        self.title = ''
        self.desc = ''
        self.main_url = kwargs.pop('main_url', '')

        # if url is missinng path segment, ensure it is set to '/'
        try:
            parts = list(urlsplit(self.main_url))
            if not parts[2]:
                parts[2] = '/'
                self.main_url = urlunsplit(parts)
        except:
            pass

        self.detect_pages = kwargs.get('detect_pages')
        self.referrers = set()

    def process_index_entry(self, it, record, *args):
        type_ = record.rec_headers.get('WARC-Type')
        if type_ == 'warcinfo':
            self.parse_warcinfo(record)

        elif type_ in CDXJIndexer.DEFAULT_RECORDS:
            if type_ in ('response' 'resource'):
                self.extract_text(record)

            super().process_index_entry(it, record, *args)


    def process_all(self):
        super().process_all()

        if self.detect_pages:
            to_delete = [id_ for id_, value in self.pages.items() if value['url'] not in self.referrers]
            for delete in to_delete:
                del self.pages[delete]

            print('Num Pages Detected: {0}'.format(len(self.pages)))

    def _do_write(self, urlkey, ts, index, out):
        if self.detect_pages:
            self.detect_page(ts, index)

        super()._do_write(urlkey, ts, index, out)

    def detect_page(self, ts, index):
        referrer = index.get('referrer')
        if referrer:
            self.referrers.add(referrer)

    def _read_record(self, record):
        if hasattr(record, 'buffered_stream'):
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
        warcinfo_buff = warcinfo_buff.decode('utf-8')
        metadata = None
        for line in warcinfo_buff.rstrip().split('\n'):
            parts = line.split(':', 1)
            if parts[0] == 'json-metadata':
                metadata = json.loads(parts[1])
            elif len(parts) == 2:
                warcinfo[parts[0]] = parts[1].strip()

        if not metadata:
            return

        if metadata['type'] == 'collection':
            self.title = metadata.get('title', '')
            self.desc = metadata.get('desc', '')

        elif metadata['type'] == 'recording':
            pages = metadata.get('pages', [])
            for page in pages:
                id_ = page['timestamp'] + '/' + page['url']
                self.pages[id_] = page

        self.detect_pages = False

    def extract_text(self, record):
        url = record.rec_headers.get('WARC-Target-URI')
        date = record.rec_headers.get('WARC-Date')
        ts = iso_date_to_timestamp(date)
        id_ = ts + '/' + url

        if self.main_url and url == self.main_url:
            print('Found Main Url: {0}'.format(url))
            self.pages[id_] = {'timestamp': ts, 'url': url, 'title': url}

        mime = self.get_record_mime_type(record)

        if mime not in HTML_MIME_TYPES:
            return

        status = record.http_headers.get_statuscode()
        if record.http_headers and status.startswith('3'):
            return

        if id_ not in self.pages:
            if self.detect_pages:
                self.pages[id_] = {'timestamp': ts, 'url': url, 'title': url}
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
        yield '!meta 0 ' + json.dumps({'format': 'cdxj-pages-1.0', 'title': 'All Pages'})

        for line in pages.values():
            ts = timestamp_to_iso_date(line['timestamp'])
            title = quote(line.get('title') or line.get('url'), safe=':/?&=')

            data = {'url': line['url']}
            if 'text' in line:
                data['text'] = line['text']

            yield title + ' ' + ts + ' ' + json.dumps(data)

    def serialize_json_pages(self, pages):
        yield json.dumps({'format': 'json-pages-1.0', 'title': 'All Pages'}) + "\n"

        for line in pages.values():
            ts = timestamp_to_iso_date(line['timestamp'])
            title = line.get('title')

            data = {'url': line['url'], 'ts': ts}
            if title:
                data['title']= title

            if 'text' in line:
                data['text'] = line['text']

            yield json.dumps(data) + "\n"

    def generate_metadata(self, res):
        desc = res.desc or self.desc
        title = res.title or self.title
        textIndex = PAGE_INDEX if res.text else ''

        data = {}
        if title:
            data['title'] = title

        if desc:
            data['desc'] = desc

        if textIndex:
            data['textIndex'] = textIndex

        data['pages'] = [
            {'title': page.get('title') or page.get('url'),
             'date': timestamp_to_iso_date(page['timestamp']),
             'url': page['url']} for page in self.pages.values()]

        return yaml.dump(data)

