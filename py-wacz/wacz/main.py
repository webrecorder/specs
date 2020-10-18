from argparse import ArgumentParser
from io import BytesIO, StringIO, TextIOWrapper
import os, datetime, tempfile, shutil, zipfile, sys, gzip
from wacz.waczindexer import WACZIndexer, PAGE_INDEX
from frictionless import File, describe_package, helpers
from wacz.util import support_hash_file

"""
WACZ Generator 0.1.0
"""

def main(args=None):
    parser = ArgumentParser(description='WACZ creator')

    parser.add_argument('inputs', nargs='+')
    parser.add_argument('-o', '--output', default="archive.wacz")

    parser.add_argument('-t', '--text', help='Generate experimental full-text index', action='store_true')

    parser.add_argument('--detect-pages', action='store_true')

    parser.add_argument('--url')
    parser.add_argument('--date')
    parser.add_argument('--title')
    parser.add_argument('--desc')

    res = parser.parse_args(args)
    wacz = None
    try:
        wacz = create_wacz(res)
    finally:
        if wacz:
            wacz.close()

def now():
    return tuple(datetime.datetime.utcnow().timetuple()[:6])

def is_safe_path(path):
    return True

def create_wacz(res):
    wacz = zipfile.ZipFile(res.output, 'w')
    helpers.is_safe_path = is_safe_path
    tmpdir = tempfile.mkdtemp()

    print('Generating indexes...')

    # write index
    data_file = zipfile.ZipInfo("data/indexes/index.cdx.gz", now())

    index_file = zipfile.ZipInfo("data/indexes/index.idx", now())
    index_file.compress_type = zipfile.ZIP_DEFLATED

    index_buff = BytesIO()

    text_wrap = TextIOWrapper(index_buff, "utf-8", write_through=True)

    wacz_indexer = None
    with wacz.open(data_file, 'w') as data:
        wacz_indexer = WACZIndexer(text_wrap, res.inputs, sort=True, compress=data,
                                   fields='referrer',
                                   data_out_name='index.cdx.gz', records='all',
                                   main_url=res.url,
                                   detect_pages=res.detect_pages)

        wacz_indexer.process_all()
    index_buff.seek(0)

    with wacz.open(index_file, 'w') as index:
        shutil.copyfileobj(index_buff, index)

    # write archives
    print('Writing archives...')
    for _input in res.inputs:
        archive_file = zipfile.ZipInfo.from_file(_input, "data/archive/" + os.path.basename(_input))
        with wacz.open(archive_file, 'w') as out_fh:
            with open(_input, 'rb') as in_fh:
                shutil.copyfileobj(in_fh, out_fh)
                path = "data/archive/" + os.path.basename(_input)

    if res.text:
        print('Generating text index...')
        # generate pages/text
        pages_file = zipfile.ZipInfo(PAGE_INDEX, now())
        pages_file.compress_type = zipfile.ZIP_DEFLATED

        with wacz.open(pages_file, 'w') as pg_fh:
            for line in wacz_indexer.serialize_json_pages(wacz_indexer.pages):
                pg_fh.write(line.encode("utf-8"))
    
   # generate metadata
    print('Generating metadata...')
    tmpdir = tempfile.mkdtemp()
    for file in wacz.infolist():
        content = wacz.read(file.filename)
        path = os.path.join(tmpdir, file.filename.replace("/", "_"))
        
        if ".gz" not in path:
            with open(path, "wb") as tmp:
                tmp.write(content)
        if ".gz" in path:
            with open(path, "wb") as tmp:
                 gzip_file = gzip.GzipFile(mode='wb', fileobj=tmp)
                 gzip_file.write(content)
                 index_cdx_hash = support_hash_file(content)
                 index_cdx_bytes = len(content)
                 gzip_file.close()

    metadata = wacz_indexer.generate_metadata(res, tmpdir, index_cdx_hash, index_cdx_bytes)
    metadata_file = zipfile.ZipInfo("datapackage.json", now())
    metadata_file.compress_type = zipfile.ZIP_DEFLATED
    wacz.writestr(metadata_file, metadata.encode("utf-8"))
    shutil.rmtree(tmpdir)
    return wacz

if __name__ == "__main__":
    main()

