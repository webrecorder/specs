# WACZ Signing/Verification Specification 0.1.0


## Introduction

This document is a working draft for a proposal to create signed WACZ packages which allow the packages author to be cryptographically proven.

The specification is an addendum to he main [WACZ Specification](https://webrecorder.github.io/wacz-spec/)

### Motivation

The purpose of this specification is to provide an optional mechanism to make web archives bundled in WACZ more trusted.

The WACZ format provides a way to create portable web archives and distribute them through any online network in a decentralized manner.

To increase trust in web archives, it becomes necessary to guarantee certain properties about who the web archive was created and when.

### Provenance of Authenticity

Proving web archive authenticity can be difficult. Ideally, proof of authenticity could guarantee that any web server served a particular URL at a particular point in time.
Unfortunately, this is not currently possible with existing web standards, as even TLS does not provide "non-repudiation".

There are proposals, such as [signed exchanges](https://wicg.github.io/webpackage/draft-yasskin-http-origin-signed-responses.html), which provide new ways for web servers to serve content that could later be verified. However, this requires HTTPS servers to support a new protocol and format.

A web archive can can be created by any HTTP client that is capable of recording its end of the HTTP network traffic. The goal of this specification is to provide a way for a client that creates a web archive and stores it in the WACZ format to also add authentication information.

This proposal will provide a mechanism to authenticate:
- an identity for the creator of the web archive
- a timestap for when the web archive was created

This approach requires trusting the client, and possible trusted third party 'observer' that signs the web archive.

(This proposal does not make any guarantees from the perspective of the web server serving the content, as this is not currently possible with HTTP/S)


## WACZ Signature File and Format

The WACZ format builds on top of the [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/). The data package includes a manifest `datapackage.json` file which contains the hashes of all the files in the data package.

A signed WACZ also contains a `datapackage-digest.json`, which contains a hash and signature of the `datapackage.json`

(Note: While this specification is primarily designed for WACZ files, the approach described here may be adapted to any Frictionless Data Package-based specification)

### `datapackage-digest.json` File

The `datapackage-digest.json` file, included in the root of the WACZ file, contains the following structure:

```
{
  "path": "datapackage.json",
  "hash": "<sha256 hash of datapackage.json>"
  "signedData": <SignatureData struct>
}
```

### Signature Data Format

The SignatureData structure is the output of the signing operation contains be one of the following formats,
a signature with a public key, which requires external key management, and a certificate signed signature,
which can be validated by publicly available certificates.


#### Anonymous Signature

```
{
    // input hash to sign
    "hash": "<sha256 hash of datapackage.json>,
  
    // metadata info
    "created": "<ISO 8861 Date>",
    "software": "<string>",
    "version": "<string>",
  
    // signature of hash
    "signature": "<base64 encoded signature>",
  
    // public key of keypair used to created the signature
    "publicKey": "<base64 encoded public key (ECDSA) >",
}
```

With this approach, the WACZ contains just enough to validate that they signature with the `publicKey`.
  
To validate authorship of the WACZ, external key management is required, and this signature is otherwise anonymous.
  
Currently, this approach is used in decentralized tooling, such as the ArchiveWeb.page extension.
  

#### Domain-Ownership Identity + Signed Timestamp

```
{
    // input hash to sign
    "hash": "<sha256 hash of datapackage.json>,
  
    // metadata info
    "created": "<ISO 8861 Date>",
    "software": "<string>",
    "version": "<string>",
  
    // signature of 'hash' by domainCert
    "signature": "<base64 encoded signature>",
    "domain": "<valid hostname>",
    "domainCert": "<PEM certificate chain>",
  
    // signature of 'signature' by timestampCert
    "timeSignature": "<base64 encoded signature>",
    "timestampCert": "<PEM ceriticate chain>",
    
    // optional: cross-signing cert for "signature"
    "crossSignedCert": "<PEM certificate chain>"
}
```

This approach allows for the WACZ signature to be created by the same private key as is used to create a TLS certificate for a particular domain.
  
The creator of the WACZ file is the same as the owner of a particular TLS certificate, which can be explored via Certificate Transparency logs.

This approach also includes an RFC 3161 timestamp server `timeSignature` of the first `signature`.

The `timeSignature` includes the timestampped and is designed to further guarantee that the signature was created close to the specified creation time.

For additional verification, an optional `crossSignedCert` can be provided which can be used as an alternative to the `domainCert`, in case the domain
certificate has been found to be compromised for any reason. The cross-signed certificate simply provides a way to provide an alternative trust path 
not tied to the domainCert, if it becomes needed for any reason.

The `domainCert`, `timestampCert`, and `crossSignedCert` should include the full certificate chain to aide in validation.

## Signing

To generate the `signatureData`, the creator of the WACZ can perform the following steps.

### Anonymous Signing

At minimum, the creator of the WACZ can create the anonymous signature `signatureData`, containing only its public key and signature.

With this approach, the client must distribute its public key out-of-band to make WACZ verification possible.

### Domain-Name Identity + Timestamp Signing

To create the signatureData in the second example, the client must perform the following:

1) Generate a ECDSA private key.
2) Create a Certificate Request signed by the private key.
3) Receive a TLS certificate for its CSR from a trusted CA, such as LetsEncrypt.
4) Optionally: use a second CA (such as a private self-signed CA) to generate a second cross-signed certificate as backup.
5) Sign the hash using its private key to generate the first signature (signature)
6) Use an RFC 3161 timestamp server to sign the previous signature (timeSignature)

This approach is based on a 'trusted-third party' which securely creates and signs the WACZ files.

The intended workflow for this approach is that the creator of the WACZ has a secure, private connection
to the attestation server which is running on the designated domain and can observe and sign the requested hash.
Access to the attestation server must be restricted to trusted creator of the WACZ.
Establishing this secure connection is beyond the scope of this specification.


## Verification

Verification of a signed WACZ can involve the following steps:

1) Validate the WACZ as a Frictionless Data Package, ensuring the `datapackage.json` hashes match the contents.
2) Validate that the `hash` in `datapackage-digest.json` matches `datapackage.json`.

### Anonymous Signature Validation

Given an anonymous `signatureData` with only a publicKey:

3) Validate the `signature` of the specified `hash` with the `publicKey`.

The WACZ file is thus valid, but publicKey must be validated using external mechanisms.

### Domain-Name Identity + Timestamp Validation.

Given a signature data with domain-name signature + timestamp, the validation is as follows:

3) Read the first certificate in `domainCert` certificate chain and validate that `signature` is a valid signature of `hash` using the public key
of the certificate.
4) Verify that the `domain` matches the subjectName of the `domainCert` TLS certificate.
5) Read the first certificate of `timestampCert` certificate chain and validate that the `timeSignature` is a valid RFC 3161 timestamp signature of 
`signature`
6) Validate that the `created` date is within 10 minutes of the signed timestamp in `timeSignature`
7) Verify trust of the `domainCert` certificate chain by checking trusted root list. (Optionally, check for certificate revokation in Certificate Transparency logs).
8) Verify trust of the `timestampCert` certificate chain by checking trusted root list.
9) Optional: if `crossSignedCert` is provided, check that it has same public key as `domainCert`, and check this chain in trusted root list. Or, if `domainCert` is not trusted, use this trust path instead of `domainCert`.


### Verification of Partially loaded WACZ

The verification process above assumes a fully loaded WACZ file. However, WACZ format supports partial loading of individual HTTP responses (via WARC records) on demand.

For partial/on-demand loading, step 1) is modified as WARC files are not fully loaded and can not be validated against the hash.

Insetad, for each WARC record, verify the hash of the loaded WARC record with the hash specified in the CDXJ index.
If using a compressed CDXJ index, also verify the hash of each compressed CDXJ block with the IDX index.
(See the CDXJ specification for more details).

## Implementations

Implementations of this spec exist in the following tools:

* The [authsign](https://github.com/webrecorder/authsign) library provides an HTTP-based API for creating and validating a WACZ `signatureData` for the domain-name identity + timestamp approach. This  library uses the LetsEncrypt service to generate a domain certificate on-demand, and the [FreeTSA](https://freetsa.org/index_en.php) timestamping service to generate an RFC 3161 timestamp.

* The [py-wacz](https://github.com/webrecorder/py-wacz) CLI tool can be used to generate and validate WACZ file with domain-name identity + timestamp, by either connecting to a `authsign` server via API for signing, or for validating directly via the CLI.

* The [ArchiveWeb.page](https://archiveweb.page) extension produces signed WACZ files with an anonymous `signatureData`. The publicKey is not yet distributed outside the extension.


### Acknowledgments

The development of this specification was supported by and developed in collaboration with Harvard Law Library Innovation Lab (Harvard LIL).



