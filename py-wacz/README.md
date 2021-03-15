## py-wacz

This directory contains the beginning of a new tool to create WACZ files in python.
It is designed to be in sync with the WACZ format specification.

It supports converting any WARC files into WACZ files, and optionally generating full-text search indices of pages.

WARCs created with Webrecorder and Conifer already contain additional metadata, such as a list of pages for the WACZ file.

For other WARCs, pages can also be detected by guessing which URLs are pages with the `--detect-pages` flag.
Alternatively, a page list can be specified (in newline-delimeted JSON form) with the `--pages` flag.


To use, run:

```
python setup.py install

wacz create -o myfile.wacz <path/to/WARC>
```
For a complete list of options, run `wacz create -h`

The resulting `myfile.wacz` should be loadable via [ReplayWeb.page](https://replayweb.page)

You can also validate an existing wacz file by running

```
wacz validate myfile.wacz
```
### Available Flags
wacz has two main functions, ```create``` and ```validate``` these sections explain the flags available under each.

#### Validate
-------

`-f --file`

Explicitly declare the file being passed to the validate function.

```wacz validate -f tests/fixtures/example-collection.warc ```

You can also simply give the name after the create function as shown below.

```wacz validate tests/fixtures/example-collection.warc ```

-------

#### Create
-------

`-f --file`

Explicitly declare the file being passed to the create function.

```wacz create -f tests/fixtures/example-collection.warc ```

You can also simply give the name after the create function as shown below.

```wacz create tests/fixtures/example-collection.warc ```

-------
`-o --output`

Explicitly declare the name of the wacz being created

```wacz create tests/fixtures/example-collection.warc -o mywacz.wacz```

-------
`-t --text`

Generates pages.jsonl page index with a full-text index, must be run in conjunction with --detect-pages. Will have no effect if run alone

```wacz create tests/fixtures/example-collection.warc -t```

-------
`--detect-pages`

Generates pages.jsonl page index without a full-text index

```wacz create tests/fixtures/example-collection.warc --detect-pages```

-------
`-p --pages`

Overrides the pages index generation with the passed jsonl pages.

```wacz create tests/fixtures/example-collection.warc -p passed_pages.jsonl```

You can add a full text index by including the --text tag

```wacz create tests/fixtures/example-collection.warc -p passed_pages.jsonl --text```

-------
```  --ts ```

Overrides the ts metadata value in the datapackage.json file

```wacz create tests/fixtures/example-collection.warc --ts TIMESTAMP```

-------
```  --url ```

Overrides the url metadata value in the datapackage.json file

```wacz create tests/fixtures/example-collection.warc --url URL```

-------
```  --title ```

Overrides the titles metadata value in the datapackage.json file

```wacz create tests/fixtures/example-collection.warc --title TITLE```

-------
```  --desc ```

Overrides the desc metadata value in the datapackage.json file

```wacz create tests/fixtures/example-collection.warc --desc DESC```

-------
 
```  --hash-type ```
  Allows the user to specify the hash type used. Currently we allow sha256 and md5

```wacz create tests/fixtures/example-collection.warc --hash-type md5```

-------
