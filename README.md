# Webrecorder Specifications

This repository contains technical specifications used by the [Webrecorder] project for building interoperable web archiving tools. Please help us adapt and implement them to ensure that web archives are easier to use, trust, and share on the web.

* [Use Cases for Decentralized Web Archives]: a summary of requirements and potential threat models for distributed web archives
* [Web Archive Collection Zipped (WACZ)]: a packaging standard for web archives on the web
* [WACZ Signing and Verification]: the mechanics for signing and verifying WACZ files for proof of authenticity
* [Crawl Index JSON (CDXJ)]: an extensible format for WARC index files

[Webrecorder]: https://webrecorder.net
[Web Archive Collection Zipped (WACZ)]: https://specs.webrecorder.net/wacz/latest/
[Use Cases for Decentralized Web Archives]: https://specs.webrecorder.net/use-cases/latest/
[WACZ Signing and Verification]: https://specs.webrecorder.net/wacz-auth/latest/
[Crawl Index JSON (CDXJ)]: https://specs.webrecorder.net/cdxj/latest/

## Viewing Locally

Webrecorder's spec website is built with [ReSpec](https://respec.org/).  The only requirement is that you run a web server locally to view the site as you develop it.

1. Download a simple web server like [http-server](https://github.com/http-party/http-server).
2. Run the web server in the repo root directory.