# WACZ 1.1.1 / py-wacz 0.3.0

- Add `name` field to `resources` for better compatibility with frictionless spec.

# WACZ 1.1.0 / py-wacz 0.3.0b1

Improved compatibility with frictionless data spec
- Each resource has a prefixed `hash` field and a `bytes` field.
- Remove separate `metadata` block.
- Support for `datapackage-digest.json`, which contains a `hash` of the `datapackage.json` (and is not included in datapackage.json)

## py-wacz 0.3.0 specific:
- Top-level `title`, `description`, `created`, `software` fields and optional `mainPageURL` and `mainPageTS` fields.
- Include full WARC record digests in `recordDigest` field in CDX, `digest` in IDX
- Support for `pages/extraPages.jsonl` passed in via --extra-pages/-e flag
