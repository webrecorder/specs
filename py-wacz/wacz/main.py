from argparse import ArgumentParser, RawTextHelpFormatter
from io import BytesIO, StringIO, TextIOWrapper
import os, datetime, shutil, zipfile, sys, gzip, pkg_resources
from wacz.waczindexer import WACZIndexer
from wacz.util import now, WACZ_VERSION
from frictionless import validate
from wacz.validate import Validation, OUTDATED_WACZ

"""
WACZ Generator 0.2.0
"""

PAGE_INDEX = "pages/pages.jsonl"

PAGE_INDEX_TEMPLATE = "pages/{0}.jsonl"


def main(args=None):
    parser = ArgumentParser(
        description="WACZ creator", formatter_class=RawTextHelpFormatter
    )

    parser.add_argument("-V", "--version", action="version", version=get_version())

    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    create = subparsers.add_parser("create", help="create wacz file")
    create.add_argument("inputs", nargs="+")
    create.add_argument("-f", "--file", action="store_true")

    create.add_argument("-o", "--output", default="archive.wacz")

    create.add_argument(
        "-t",
        "--text",
        help="Generates pages.jsonl with a full-text index",
        action="store_true",
    )

    create.add_argument(
        "--detect-pages",
        help="Generates pages.jsonl without a text index",
        action="store_true",
    )

    create.add_argument(
        "--hash-type",
        choices=["sha256", "md5"],
        help="Allows the user to specify the hash type used. Currently we allow sha256 and md5",
    )

    create.add_argument("--ts")
    create.add_argument("--url")
    create.add_argument("--date")
    create.add_argument("--title")
    create.add_argument("--desc")
    create.set_defaults(func=create_wacz)

    validate = subparsers.add_parser("validate", help="validate a wacz file")
    validate.add_argument("-f", "--file", required=True)
    validate.set_defaults(func=validate_wacz)

    cmd = parser.parse_args(args=args)

    if cmd.cmd == "create" and cmd.ts is not None and cmd.url is None:
        parser.error("--url must be specified when --ts is passed")

    value = cmd.func(cmd)
    return value


def get_version():
    return (
        "%(prog)s "
        + pkg_resources.get_distribution("wacz").version
        + " -- WACZ File Format: "
        + WACZ_VERSION
    )


def validate_wacz(res):
    validate = Validation(res.file)
    version = validate.version
    validation_tests = []

    if version == OUTDATED_WACZ:
        print("Validation Succeeded the passed Wacz is outdate but valid")
        return 0

    elif version == WACZ_VERSION:
        validation_tests += [
            validate.check_required_contents,
            validate.frictionless_validate,
            validate.check_file_paths,
            validate.check_file_hashes,
        ]
    else:
        print("Validation Failed the passed Wacz is invalid")
        return 1

    for func in validation_tests:
        success = func()
        if success is False:
            print("Validation Failed the passed Wacz is invalid")
            return 1

    print("Validation Succeeded the passed Wacz is valid")
    return 0


def create_wacz(res):
    wacz = zipfile.ZipFile(res.output, "w")

    print("Generating indexes...")

    # write index
    data_file = zipfile.ZipInfo("indexes/index.cdx.gz", now())

    index_file = zipfile.ZipInfo("indexes/index.idx", now())
    index_file.compress_type = zipfile.ZIP_DEFLATED

    index_buff = BytesIO()

    text_wrap = TextIOWrapper(index_buff, "utf-8", write_through=True)

    wacz_indexer = None
    with wacz.open(data_file, "w") as data:
        wacz_indexer = WACZIndexer(
            text_wrap,
            res.inputs,
            sort=True,
            compress=data,
            fields="referrer",
            data_out_name="index.cdx.gz",
            records="all",
            hash_type=res.hash_type,
            main_url=res.url,
            main_ts=res.ts,
            detect_pages=res.detect_pages,
            extract_text=res.text,
        )

        wacz_indexer.process_all()

    index_buff.seek(0)

    with wacz.open(index_file, "w") as index:
        shutil.copyfileobj(index_buff, index)

    # write archives
    print("Writing archives...")
    for _input in res.inputs:
        archive_file = zipfile.ZipInfo.from_file(
            _input, "archive/" + os.path.basename(_input)
        )
        with wacz.open(archive_file, "w") as out_fh:
            with open(_input, "rb") as in_fh:
                shutil.copyfileobj(in_fh, out_fh)
                path = "archive/" + os.path.basename(_input)

    if len(wacz_indexer.pages) > 0:
        print("Generating page index...")
        # generate pages/text
        wacz_indexer.write_page_list(
            wacz,
            PAGE_INDEX,
            wacz_indexer.serialize_json_pages(
                wacz_indexer.pages.values(),
                id="pages",
                title="All Pages",
                has_text=wacz_indexer.has_text,
            ),
        )

    if len(wacz_indexer.extra_page_lists) > 0:
        print("Generating extra page lists...")

        for name, pagelist in wacz_indexer.extra_page_lists.items():
            if name == "pages":
                name = shortuuid.uuid()
            filename = PAGE_INDEX_TEMPLATE.format(name)

            wacz_indexer.write_page_list(wacz, filename, pagelist)

    # generate metadata
    print("Generating metadata...")

    metadata = wacz_indexer.generate_metadata(res, wacz)
    metadata_file = zipfile.ZipInfo("datapackage.json", now())
    metadata_file.compress_type = zipfile.ZIP_DEFLATED
    wacz.writestr(metadata_file, metadata.encode("utf-8"))
    return 0


if __name__ == "__main__":
    main()
