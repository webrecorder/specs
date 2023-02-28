# WACZ/WARC on IPFS Spec

## Abstract

This specification details how WACZ/WARC files can be uploaded to IPFS using custom content-aware chunking strategies and the UnixFS standard. We do this by inspecting the boundries inside a WACZ file for the individual archived pages and use that to form a UnixFS DAG when uploading an archive to IPFS.

## Conformance

As well as sections marked as non-normative, all authoring guidelines, diagrams, examples, and notes in this specification are non-normative. Everything else in this specification is normative.
The key words MAY and MUST in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals, as shown here.

## Terminology

- IPFS
- UnixFS
- Content Addressing
- Peer to Peer Networks: Software protocols for connecting people's computers directly together without a server acting as an intermediary.
- Chunking
- WACZ
- WARC

## Introduction

### Motivation

Web archiving is important for preserving cultural information and in order to add even more resilence to archives, they can be uploaded to peer to peer protocols (P2P) in order to make backup and retrieval more seamless.
Along with uploading content to be shared, P2P protocols enable us to interact with the data itself in new ways by chaging the way archive files are stored on disk and transmitted accross a network.
This specification formalizes what we learned and goes over the benefits of doing so.

### Deduplication

One of the advantages of using content addressible systems like IPFS is that datasets which contain the same data will de-duplicate storage for that data when within a larger dataset.
A lot of web content is ripe for deduplication where JavaScript files, Fonts, Images, and Videos might be embedded within different pages.
Typically, when storing archival datasets without content addressing, all of these resources will be doubled up on disk.

## UnixFS File Chunking

The [UnixFS specification](https://github.com/ipfs/specs/blob/main/UNIXFS.md) allows for individual files to be "chunked" by separating continuous segments of the file's data into individual nodes in a Merkle DAG. These intermediate nodes are themselves encoded as UnixFS files.

Readers of UnixFS files will automatically detect when a file has been chunked in this way, and will convert the UnixFS DAG to a representation where all the contents are treated as one continuous stream which can be randomly accessed at any index.

The interesting property here is that we can artifically create these chunked DAGs by concatenating preexisting UnixFS file nodes into one.

This enables us to stitch together files while preserving their individual DAGs and being able to deduplicate content in the same way as if those files were uploaded on their own.

TODO: Make examples of UnixFS DAGs with meta code on how they connect

The process involes uploading your raw files to their own UnixFS DAGs, getting the sizes of the individual files as well as the Content IDs (CID) for the data and then combining them in a UnixFS file via it's `Links` using the DAG-PB codec.

## ZIP File Chunking

The [ZIP file format](https://www.loc.gov/preservation/digital/formats/fdd/fdd000354.shtml) is used to create a single file which can contain several files within a directory structure. It allows files to be stored compressed and in their raw uncompressed form as continuous segments of the file.

We can combine this with our custom chunking code in order to chunk a ZIP file at it's file boundries and generate regular UnixFS file nodes for the file chunks in the same way that they would be generated on their own.

TODO: Diagram showing file boundries in a zip file, and chunk boundries in a UnixFS Dag

## WARC File Chunking

WARC files contain a series of "Records" for loaded resources.

We group these records into individual UnixFS File DAGs so that they can more easily be recombined between archives at the UnixFS level.

TODO: Diagram of file with deliniation for records. The 'type' of record can be seen and the request and response records are grouped together (outline with a box?)

As well, we make sure to split out the response body into its own DAG node so that its contents may be deduplicated accross all archives and IPFS content.

## WACZ File Chunking

The WACZ file format is based on the ZIP file format with the addition of a WARC file for archival data, and some extra files for viewing the data.

TODO: Diagram of directory structure within WACZ with the files usually added by WebRecorder tools

We take advantage of this by reading the metadata from the WACZ and WARC files and creating additional chunking boundries at the boundries of individual files within the WARC file.

TODO: Diagram of WACZ IPLD structure. Show ranges of zip files and the end directory structure, make boxes around IPLD boundries with labels.

Due to how UnixFS file DAGs can be nested indefinately, we can build up the merkle DAG for the WARC file separately and embed it into the DAG of the ZIP file itself.

Once a file has been chunked, any resources that have the same data within the archive or within other archives will get deduplicated at the storage / loading layer.

## Algorithm

This algorithm is used for generating a UnixFS file tree for a single WACZ file which contains a webarchive.

This spec uses shorthands for referencing the UnixFS spec, and implementers should follow that spec in order to properly construct UnixFS Dag-PB blocks.
Shorthands are also used when referring to the ZIP file structure such as parsing out headers or the final directory block.
This spec relies on the existence of a blockstore to `put()` blocks of data into and get back the `cid` for the data.
This could be an on-disk or in-memory repo, or a streaming CAR file generation library.

- Create a root UnixFS.File entity representing the entire archive
- Create a UnixFS.Dir entity representing the ZIP root `zip`
- Iterate through each entry in the zip file
	- Get the buffer for the headers
	- Create a UnixFS.File (`headerFile`) and write the header buffer to it's `data` property
	- Encode the `headerFile` entry into Dag-PB
	- `put()` the `headerFile`  into the blockstore and get back the `cid` and `block size`.
	- Get the `file name` from the header
	- Append a new `link` to the `zip` Dir with the `cid` and `block size` (Make sure the `blocksizes` property gets updated)
	- Get the  and `cid` of the headers file and append it to the `zip` UnixFS.Dir
	- // TODO: Account for subdirectories in the UnixFS DAG
	- If the `file name` ends in `.warc`
		- TODO: WARC-Specific Chunking
		- Generate a root `UnixFS.File` for the `warc` file
		- Generate a `UnixFS.File` (`recocrdFile`)
		- Iterate through each record
			- Create a new `UnixFS.File` for the `record`
			- Add bytes up until the first `Response` record
			- Turn response reocordd data into its own `UnixFS.File` (`responseDataFile`) (note that applications should decide on a consistent chunking size here)
			- `put()` `responseDataFile` and add it's `cid` and `file size` to the `reocrd`
			- Add rest of the bytes in the record (if they exist)
			- `put()` the record and append it to the `warc` file with it's size.
  - Else
  	- Create a new UnixFS.File (`file`)
  	- Parse the `last modified time / date` from the header
  	- Write the rest of the entry data to the `file` (Note that applications should decide on a consistent chunking size here)
  	- Encode the `file` and `put()` it into the blockstore to get back the `cid` and `block size`.
  	- Also get the overall `file size`
  	- Append a new `link` to the `zip` dir with the `cid` and `file size`
- Get the overall `file size` from the `zip` dir
- Create a UnixFS.File entries for the following contents within the ZIP file:
 - `pages/pages.jsonl'
 - `indexes.cdx` or `indexes/index.cdz.gz` and `indexes/index.idx`
- Create a UnixFS.File for the WARC file
- While iterating through the WARC file records
  - Load the data warc contents into the file and get it's CID
  - Append the CID to the `Links` for the WARC file
- Append the `archive/data.warc` file with the CID of the WARC file

## Implementations

https://github.com/webrecorder/ipfs-composite-files#in-place-zip

https://github.com/webrecorder/awp-sw/blob/ed11bcecef16180236c752075011907ff88e40e1/src/ipfsutils.js#L463
