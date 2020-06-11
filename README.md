# Web Archive Collection Format

This document is working draft/proposal for a directory structure + ZIP format specification for sharing and distributing web archives. ZIP files using this format can be referred to as WACZ (Web Archive Collection Zipped).

Feedback on this proposal is *strongly encouraged!*.

Please open github issues with any thoughts/suggestions/comments.


## Motivation

The goal of this spec is to provide an interoperable way to share web archive *collections*,
additional data necessary to make web archives useful to humans.

To make sense and use a web archive, it is necessary to have more than just the raw HTTP request/response data,
yet no standardized format exists to include all the data that is needed.

In particular, a web archive collection should have:
- A random-access index of all raw data (preferrably accessible with minimal seek)
- A set of pages, entry point URLs from which users should browse the web archive. 
- Other user-defined, editable metadata about the web archive collection (title, description, etc...)

The spec is not designed to replace any other format, but to set up a convention-based format to bundle this data together
via directory layout.

The spec consists of:

1) A extensible directory layout for web archive data
2) A specification for bundling the directory layout in a ZIP file.


## The Directory Layout

The spec is to designate a mostly flat directory structure which can contain different types of web archive collection data:

```
- archive/
- indexes/
- webarchive.yaml
- pages.csv
- derivatives/
```

The directory can further be bundled into a ZIP file.

### Directories and Files

 
#### 1) `archive/` (required)
 
The archives directory can contain raw web archive data.
This can be in a variety of formats, including WARC, ARC, as well as other formats that support
random access, (eg. ZIM)

Possible formats:
- WARC (.warc, .warc.gz)
- ARC (.arc, .arc.gz)
- ZIM (.zim)
- HAR? (.har)
- Web Bundle? (.wbn)


 
#### 2) `indexes/` (required)
 
 The indexes directory should include various indexes into the raw data stored in `archives/`
 
 Currently possible index formats include:
 - CDX (.cdx, .cdxj) for raw text-based binary sorted indices
 - Compressed CDX (.cdx.gz and .idx) indices
 
#### 3) `webarchive.yaml` (optional)

This file serves as the manifest for the web archive and can contain at least the following fields.

All keys are optional. 

Keys specified in this file take precedent over other files, and provide a way to override the configuration
of the web archive.

```yaml
title: 'Title of Collection'
desc: 'Description of Collection'
pages: <list of pages>
pageLists: <list of page lists>
```

##### `pages` key

pages is a list of 'Page' objects, each containing at least the following fields:

- `url` - a valid URL (or URI/URN?)
- `date` - a valid ISO 8601 Date string
- `title` - any string or omitted
- `id` - any string or omitted.

Ex:
```yaml
pages:
  - url: https://example.com/
    date: 2020-06-11T04:56:41Z
    title: 'Example Domain'
    id: '123'
    
  - url: https://another.example.com/
    date: 2020-06-26T01:02:03Z
    id: '456'
```


##### `pageLists` key (optiona

The `pageLists` key provides further grouping of pages into specific curatorial groups, or page lists.

Each 'PageList' can contain at least the following fields: `title`, `desc`, `id`, `pageIds`.
All fields are optional. `title, `desc`, and `id` are strings.

`pageIds` is a list of page ids, and each id should match a page specified in the `pages` key / file.

```yaml
pageLists:
  - title: 'Import Pages'
    desc: 'These are pages that you should definitely view in this web archive'
    id: 1
    pageIds:
       - '123'
       - 'abc'
       - '10'
```


#### 4) `pages.csv` (optional)

The list of pages, specified in a CSV format.
Each row should match the 'Page' object and contain at least the following columns: `url`, `date`, `title`, `id`
The `url` and `date` are required. The date should be in ISO 8601 format.


#### 5) `derivatives/` and other directories

Other derived data, such as screenshots, full text indices, could be placed into a general-purpose
`derivatives/` directory.

Additional ideas for standardization and possible directory formats:
- derivatives
- search indexes
- WAT / WET files
- specific metadata formats?

Perhaps extension need not be specified explicitly, as others can add directories as needed.
*Feedback wanted on this section, see https://github.com/webrecorder/web-archive-collection-format/issues/1*

Other possible ideas were suggsted in this issue: https://github.com/webrecorder/pywb/issues/319

### Precedence

Generally, keys specified in `webarchive.yaml` take precedence over data loaded by convention.

For pages, the following precedence should be used:

1) if `webarchive.yaml` `pages` key exists, pages loaded from there.
2) otherwise, if `pages.yaml` exists, pages are loaded from there.
3) otherwise, if `pages.csv` exists page are loaded from there.


## Zip Format

The entire directory structure can be stored in a standard ZIP or ZIP64 file.

The ZIP format is useful as a primary packaging of all the different formats.


### Zip Compression

Already compressed files should not be compressed again to allow for random access.

- All `/archive/` files should be stored in ZIP with 'STORE' mode.
- All `/index/*.cdx.gz` files should be stored in ZIP with 'STORE' mode.
- Text files (`*.csv`, `*.yaml`, `*.cdx`, `*.cdxj`) can be stored in the ZIP with either 'DEFLATE' or 'STORE' mode.

### Zip Format File Extension - `.wacz`

A ZIP file that follows this Web Archive Collecion format spec should use the extension `.wacz`.

Such a file can be referred to as a WACZ file or a WACZ.

<hr>

## Appendix A: Use Case: Random-Access to Web Archives in ZIP

The web archive collection format stored in a ZIP file allows for efficient random access to even very large web archives (10GB+, 100GB+, etc...). This allows for loading web archive from static storage on-demand.

The approah works as follows. Given a ZIP file, a client can quickly:
```
1) Read all entries to determine the contents of the ZIP file via random access
2) Load manifest from `webarchive.yaml`
3) Load other metadata from `pages.csv`, if any
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
This index format is in use by Internet Archcive's Wayback Machine and CommonCrawl

More Info: https://pywb.readthedocs.io/en/latest/manual/indexing.html#zipnum-sharded-index)

### HAR

The HAR format is supported by default in the DevTools of major browsers. HAR is intended for page-level archives
and is centered around page loading page metrics and browser telemetry. As a JSON-based serialization format,
it may be difficult to use for large web archiving.

HAR does include a list of entry points/pages as well as the raw resources.

More info: http://www.softwareishard.com/blog/har-12-spec/

### Web Pack/Web Bundle

The web bundle/web packaing spec attempts to solve some similar issues. Web Bundles use CBOR for serialization of HTTP request/responses, and also include an index. However, it can not be used to store existing web archive (WARC) data.

More Info: https://wicg.github.io/webpackage/draft-yasskin-wpack-bundled-exchanges.html

### ZIM

The ZIM format stores compressed files, page data and page metadata in a custom format suitable for random access loading.
The format also addresses some of the same issues raised here, but can not be used to store existing web archive data.

More Info: https://openzim.org/wiki/ZIM_file_format
