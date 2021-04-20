# Web Archive Collection Zipped (WACZ) Format

This document is working draft/proposal for a directory structure + ZIP format specification for sharing and distributing web archives. ZIP files using this format can be referred to as WACZ (Web Archive Collection Zipped).

Feedback on this proposal is *strongly encouraged!*.

Please open GitHub issues with any thoughts/suggestions/comments.

## Tools for creating WACZ

The [py-wacz](./py-wacz) subdirectory contains a proof-of-concept Python tool for creating a WACZ file from existing WARCs.


# Motivation

The goal of this spec is to provide a portable format for web archives, to address key social and technical issues:

- Social: to provide an interoperable way to share web archive *collections*, including any data necessary to make web archives useful to humans.
- Technical: to provide an efficient way to load *small amounts of data* from a remotely hosted web archive on static storage, without downloading the entire collection.

Parts of the spec are currently implemented and in use by [wabac.js](https://github.com/webrecorder/wabac.js) and [ReplayWeb.page](https://replayweb.page)

## Social: Making web archives more human friendly
To make sense and use a web archive, it is necessary to have more than just the raw HTTP request/response data,
yet no standardized format exists to include all the data that is needed.

In particular, a web archive collection should have:
- A random-access index of all raw data (preferably accessible with minimal seek)
- A set of pages, entry point URLs from which users should browse the web archive.
- Other user-defined, editable metadata about the web archive collection (title, description, etc...)

All of this data can be bundled together into a single file, using the standard ZIP format.

## Technical: Lowering the barrier to hosting large web archives

Hosting web archives currently requires complex server infrastructure, a 'wayback machine' to serve data in a way that can be viewed in the browser.

Tools like `wabac.js` provide a way to render the data directly in the browser, if it can be accessed efficiently.

The WACZ format presents a storage approach optimized for efficient random-access to large amounts of web archive data, allowing the client to load only
what is needed by seeking into a larger file (via HTTP range requests or other random access) and loading only what is needed for each page.
This is done by leveraging the ZIP format's built-in index, inclusion of an efficient web archive index (CDX or compressed CDX) along with the raw WARC data.

The spec is not designed to replace any other format, but to set up a convention-based format to bundle all necessary data together,
following a certain directory and naming convention, into a standard ZIP (or ZIP64) file.


# WACZ 1.0

The spec currently consists of the following:

1) A [frictionless data](https://frictionlessdata.io/) datapackage.json file for recording metadata.
2) A extensible directory and naming convention for web archive data
3) A specification for bundling the directory layout in a ZIP file.

The documentation is split into what is currently supported in [wabac.js](https://github.com/webrecorder/wabac.js) as stable,
experimental ideas, and possible future extensions.

## Currently Supported


#### Directory Layout

The spec is to designate a mostly flat directory structure which can contain different types of web archive collection data while conforming to the frictionless data standards.
Currently supported:

```
- archive/
- indexes/
- pages/
- datapackage.json
```

### Directories and Files


#### 1) `archive/`

The archives directory can contain raw web archive data.

Currently supported formats:
- WARC (.warc, .warc.gz)

#### 2) `indexes/`

 The indexes directory should include various indexes into the raw data stored in `archives/`

 Currently possible index formats include:
 - CDX (.cdx, .cdxj) for raw text-based binary sorted indices
 - Compressed CDX (.cdx.gz and .idx) indices

#### 3) `pages/pages.jsonl`

pages is a list of 'Page' objects, each containing at least the following fields:

- `url` - a valid URL (or URI/URN?)
- `ts` - a valid ISO 8601 Date string
- `title` - any string or omitted
- `id` - any string or omitted.
- `text` - an optional extraction of the text of the page,

Ex:
```jsonl
{"format": "json-pages-1.0", "id": "pages", "title": "All Pages"}
{"id": "1db0ef709a", "url": "https://www.example.com/page", "ts": "2020-10-07T21:22:36Z", "title": "Example Domain"}
{"id": "12304e6ba9", "url": "https://www.example.com/another", "ts": "2020-10-07T21:23:36Z", "title": "Another Page"}
```

Other `.jsonl` files can optionally be added on using the same format in the `pages/` directory.

#### 4) `datapackage.json`

This file serves as the manifest for the web archive and is compliant with the Frictionless [Data Package Specification](https://specs.frictionlessdata.io/data-package/)

The file contains the following keys:

- `profile`: Set to `data_package` in accordance with the Frictionless Data Package spec.

- `resources` is a list containing the contents of the WACZ, in accordance with the Frictionless Data Package spec.

  Ex:
   ```
    "resources": [
       {
         "path": "pages/pages.jsonl",
         "hash": "sha256:8a7fc0d302700bed02294404a627ddbbf0e35487565b1c6181c729dff8d2fff6",
         "bytes": 75
       },
       {
         "path": "archive/data.warc",
         "hash": "sha256:0e7101316ba5d4b66f86a371ee615fbd20f9d3f32d32563ed2c829db062f7714",
         "bytes": 11469796
       },
       ...
   ]
   ```

WACZ data packages can also include optional data package fields, in particular:

- `title`: Can contain title for this collection.

- `description`: Can contain description for this collection.

- `created`: ISO date string for when the WACZ file was created.


#### WACZ Specific fields

The following fields are not part of the standard data package specification and are additional fields used with WACZ:

- `wacz_version`: Should be set to `1.0.1` (or current version of WACZ). This field is required to identify the package as a WACZ.

- `mainPageURL`: An optional URL of the main or starting page in the collection, if any, to be used for initial replay.

- `mainPageDate`: An optional ISO-formatted date of the main or startng page in the collection, if any, to be used for initial replay. Specified only if `mainPageURL` is specified.


## Possible Support in the future

#### Archive formats besides WARC

It is possible that other formats, such as HAR, Web Bundle, ZIM be supported
in the `archive/` directory. (See Appendix for this formats).

#### Custom Derivatives and a general-purposes `derivatives/` directory.

Other derived data, such as screenshots, could be placed into a general-purpose
`derivatives/` directory.

Additional ideas for standardization and possible directory formats:
- derivatives
- search indexes
- WAT / WET files
- specific metadata formats?

Perhaps extension need not be specified explicitly, as others can add directories as needed.
*Feedback wanted on this section, see https://github.com/webrecorder/web-archive-collection-format/issues/1*

Other possible ideas were suggested in this issue: https://github.com/webrecorder/pywb/issues/319

## Zip Format

The entire directory structure can be stored in a standard ZIP or ZIP64 file.

The ZIP format is useful as a primary packaging of all the different formats.


### Zip Compression

Already compressed files should not be compressed again to allow for random access.

- All `archive/` files should be stored in ZIP with 'STORE' mode.
- All `index/*.cdx.gz` files should be stored in ZIP with 'STORE' mode.
- All files (`*.jsonl`, `*.json`, `*.idx`, `*.cdx`, `*.cdxj`) can be stored in the ZIP with either 'DEFLATE' or 'STORE' mode.

### Zip Format File Extension - `.wacz`

A ZIP file that follows this Web Archive Collection format spec should use the extension `.wacz`.

Such a file can be referred to as a WACZ file or a WACZ.

<hr>

## Appendix A: Use Case: Random-Access to Web Archives in ZIP

The web archive collection format stored in a ZIP file allows for efficient random access to even very large web archives (10GB+, 100GB+, etc...). This allows for loading web archive from static storage on-demand.

The approach works as follows. Given a ZIP file, a client can quickly:
```
1) Read all entries to determine the contents of the ZIP file via random access
2) Load manifest from `datapackage.json`
3) Load list of pages from `pages.jsonl`, if any
```

To lookup a given URL, such as from the page or page list:
```
1) Read the full CDX from ZIP, or read secondary secondary index (IDX)
2) Binary search index
  2a) If using compressed CDX, read compressed CDX chunk in CDX.GZ file in ZIP.
3) If index match found, get offset/length/location in WARC
4) Read compressed WARC chunk in ZIP
```

This approach is being used by https://replayweb.page/.

The implementation is in https://github.com/webrecorder/wabac.js/blob/develop/src/ziparchive.js

and is based on: https://github.com/Rob--W/zipinfo.js/blob/master/zipinfo.js



## Appendix B: Formats Referenced

This spec refers to the following formats, which could be packaged inside a Web Archive Collection structure.
Some of the formats serve similar functions, but require custom serialization and are not extensible with custom metadata.

### WARC

The WARC format is a well established standard for storing raw web archive data.

The WARC is a raw data format only, and does not have an index, or a standardized way to store entry points,
or metadata about a web archive collection.

More Info: https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/

### CDX

CDX is a plain-text, binary sorted indexing format used in web archives. CDXJ is a JSON-based
variation of CDX.

More Info: https://pywb.readthedocs.io/en/latest/manual/indexing.html#index-formats for more info.

### Compressed CDX / "ZipNum"

The Compressed CDX format uses gzip compression on top of the plain-text CDX, and a secondary
index to search the compressed index. This allows the CDX index to scale to considerably larger datasets.
This index format is in use by Internet Archive's Wayback Machine and CommonCrawl.

More Info: https://pywb.readthedocs.io/en/latest/manual/indexing.html#zipnum-sharded-index)

### HAR

The HAR format is supported by default in the DevTools of major browsers. HAR is intended for page-level archives
and is centered around page loading page metrics and browser telemetry. As a JSON-based serialization format,
it may be difficult to use for large web archiving.

HAR does include a list of entry points/pages as well as the raw resources.

More info: http://www.softwareishard.com/blog/har-12-spec/

### Web Pack/Web Bundle

The web bundle/web packaging spec attempts to solve some similar issues. Web Bundles use CBOR for serialization of HTTP request/responses, and also include an index. However, it can not be used to store existing web archive (WARC) data.

More Info: https://wicg.github.io/webpackage/draft-yasskin-wpack-bundled-exchanges.html

### ZIM

The ZIM format stores compressed files, page data and page metadata in a custom format suitable for random access loading.
The format also addresses some of the same issues raised here, but can not be used to store existing web archive data.

More Info: https://openzim.org/wiki/ZIM_file_format
