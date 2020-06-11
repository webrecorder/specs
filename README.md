# Web Archive Collection Format

This document is working draft for a directory structure / bundling format for sharing and distributing web archives.

## Motivation

The goal of this spec is to provide an interoperable way to share web archive *collections*,
beyond the raw HTTP request/response data.

A web archive collection needs to have:
- an random-access index of all raw data (preferrably accessible with minimal seek)
- a list of entry points, or groups of entry points
- other user-defined, editable metadata about the web archive collection.

The spec is not designed to replace any other format, but rather bundle them together in a coherent, but opinionated way.

## The Directory Layout

The spec is to designate a mostly flat directory structure which can contain different types of web archive collection data:

```
- archive/
- indexes/
- webarchive.yaml
```

The directory can further be bundled into a ZIP file.

### Directories/Files

#### 1) `webarchive.yaml`

This file serves as the manifest for the web archive and can contain at least the following fields:

```yaml
title: 'Title of Collection'
desc: 'Description of Collection'
pages: <list of pages>
pageLists: <list of page lists>
```
 
#### 2) `archive/` (required)
 
The archives directory can contain raw web archive data.
This can be in a variety of formats, including WARC, ARC, as well as other formats that support
random access, (eg. ZIM)

Possible formats:
- WARC (.warc, .warc.gz)
- ARC (.arc, .arc.gz)
- ZIM (.zim)
- HAR? (.har)
- Web Bundle? (.wbn)


 
#### 3) `indexes/` (required)
 
 The indexes directory should include various indexes into the raw data stored in `archives/`
 
 Currently possible index formats include:
 - CDX (.cdx, .cdxj) for raw text-based binary sorted indices
 - Compressed CDX (.cdx.gz and .idx) indices
 
 
 
 

## Appendix: Existing Formats

### WARC 

The WARC format is a well established standard for storing raw web archive data.

However, WARC is only a raw data format, not a web archive *collection* format, and is thus missing key elements
that are needed for working with web archive collection. WARC files do not have a built in index for entry points/pages.
WARCs are designed to store the raw archival data, and thus also lack a way of adding and easily modifying user metadata.

### CDX

CDX is a plain-text, binary sorted indexing format used in web archives. CDXJ is a JSON-based
variation of CDX.

See: https://pywb.readthedocs.io/en/latest/manual/indexing.html#index-formats for more info.

### Compressed CDX / "ZipNum" 

The Compressed CDX format uses gzip compression on top of the plain-text CDX, and a secondary
index to search the compressed index. This allows the CDX index to scale to considerably larger datasets.
This index format is in use by Internet Archcive's Wayback Machine and CommonCrawl

See: https://pywb.readthedocs.io/en/latest/manual/indexing.html#zipnum-sharded-index)

### HAR

The HAR format is supported by default in the DevTools of major browsers. HAR is intended for page-level archives
and is centered around page loading metrics and telemetry. As a JSON-based serialization format
and not suitable for large data, or appending new web archives. 
However, HAR does include a list of entry points/pages as well as the raw resources.

### Web Pack/Web Bundle

The web bundle/web packaing spec indeed attempts to solve some of the same issues. However, the spec is incompatible
with WARC files used by web archives, and is currently still in development.

### ZIM

The ZIM format, from Kiwix, addresses many of the same issues. The format includes entry points/pages, a searchable index,
other metadata. However, it is not a bundling format and is not compatible with existing content in other formats.
