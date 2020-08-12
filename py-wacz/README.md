## py-wacz

This directory contains the beginning of a new tool to create WACZ files in python.
It is designed to be in sync with the WACZ format specification.

Currently, it supports converting WARC files created with Webrecorder and Conifer into WACZ files, and optionally generating full-text search indices of pages.

To use, first install `pip install -r requirements.txt`, and then run:

```
python wacz.py -o myfile.wacz <path/to/WARC>
```

The resulting `myfile.wacz` should be loadable via [ReplayWeb.page](https://replayweb.page)

For a complete list of options, run `python wacz.py -h`

Note: the tool is still in development and not yet production ready.
