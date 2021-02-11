"""Registry of sources.

The `fusus` package can work with source material in arbitrary locations.

However, there is also a notion of *known works* that *fusus* has been designed for.

This is the module where those works are registered.

When new works become available, you can give them an acronym and register them here.
See `WORKS`.

At this moment, all known works reside in this repo, under subdirectory `ur`.

It is easy to run pipeline commands on known works.
Functions that deal with works can be given the acronym as an argument,
and then they know how to deal with its data:

Then you can do

``` sh
python3 -m fusus.convert tsv acro
```

This will run the OCR pipeline and deliver TSV data as result;

---

``` sh
python3 -m fusus.convert tf acro 7.3
```

This will convert the TSV data to TF and deliver the tf files in version 7.3

---

``` sh
python3 -m fusus.convert tf acro 7.3 loadonly
```

This will load the TF data in version 7.3.
The first time it loads, some extra computations will be performed, and
a binary version of the tf files will be generated, which will be used for
subsequent use by Text-Fabric.

---

See also `fusus.convert`.
"""

import os

from tf.core.helpers import unexpanduser


BASE = os.path.expanduser("~/github/among/fusus")
"""Base directory for the data files.

Currently this is the fusus repo itself.
But it could be set to different places,
if we want to separate the fusus code from the fusus data.

You might consider to make it configurable, and pass it to
the `fusus.book.Book` and `fusus.lakhnawi.Lakhnawi` objects.
"""

WORKS = dict(
    fususl=dict(
        meta=dict(
            name="fusus",
            title="Fusus Al Hikam",
            author="Ibn Arabi",
            editor="Lakhnawi",
            published="pdf, personal communication",
            period="1165-1240",
        ),
        source=dict(
            dir="ur/Lakhnawi",
            file="allpages.tsv",
        ),
        dest="tf/fusus/Lakhnawi",
        toc=True,
        ocred=False,
    ),
    fususa=dict(
        meta=dict(
            name="fusus",
            title="Fusus Al Hikam",
            author="Ibn Arabi",
            editor="Affifi",
            published="pdf, personal communication",
            period="1165-1240",
        ),
        source=dict(
            dir="ur/Affifi",
            file="allpages.tsv",
        ),
        dest="tf/fusus/Affifi",
        toc=False,
        ocred=True,
    ),
)
"""Metadata of works in the pipeline.

Here are the main works and the commentaries.

They are given a keyword, and under that keyword are these fields:

* **meta** metadata in the form of key value pairs
  that will be copied into Text-Fabric tf files;
* **source** specification of
  * **dir** directory of the work,
  * **file** the TSV data file within that directory;
* **dest** directory of the Text-Fabric data of this work;
* **toc** whether the work has a table of contents;
  this is only relevant for the Lakhnawi edition,
  which has a table of contents that requires special processing.
  This processing is hard coded.
  So it will not work for other works with a table of contents.
* **ocred** whether the work is the outcome of an OCR process;
  this is only false for the Lakhnawi edition,
  which is the result of a custom text extraction of a PDF.
  This text extraction is hard coded.
  So it will not work for other works that reside in a textual PDF.

!!! hint "fususa"
    The Affifi page images are in the `in` subdirectory of its work
    directory as specified in `WORKS`.

!!! caution "fususl"
    The Lakhnawi PDF does not reside in this repo.
    You have to obtain a copy by mailing to
    [Cornelis van Lit](mailto:l.w.c.vanlit@uu.nl) and place it
    in your repo clone as `_local/source/Lakhnawi/Lakhnawi.pdf`.

!!! hint "commentaries"
    Adding commentaries involves the following steps:

    * give a nice acronym to the commentary
    * add an entry in the source registry, keyed by that acronym
    * fill in the details
    * place the page image files in the `in` subdirectory
      that you specified under `source` and then `dir`.
"""


def getWorkDir(source, ocred):
    """Resolve a work location, given by key of directory.

    Parameters
    ----------
    source: string
        Key in the `WORKS` dictionary (*known work)*,
        or directory in the file system (*unknown work*).
    ocred: boolean or None
        Whether the work is in the OCR pipeline.
        For known works this is known, but it can be overriden.
        For unknown works it must be specified, and if not, `True`
        is assumend.

    Returns
    -------
        (string | None, boolean | None)
        If the work is known and exists, or unknown and exists,
        its working directory is returned.
        If `givenOcr` is `None`, and the work is known, its
        ocr status is returned, otherwise None.
    """
    if source not in WORKS:
        if os.path.exists(source):
            if ocred is None:
                print("Assume that {unexpanduser(source)} is OCRed")
                ocred = True
            return (source, ocred)
        else:
            if "/" in source:
                print(f"Source file `{unexpanduser(source)}` does not exist.")
            else:
                print(f"Unknown work `{source}`")
            return (None, ocred)

    workInfo = WORKS[source]

    if "source" not in workInfo:
        print(f"{source} does not specify a source")
        return (None, ocred)

    sourceInfo = workInfo["source"]

    if "dir" not in sourceInfo:
        print(f"{source} does not specify a directory in its source")
        return None

    directory = sourceInfo["dir"]
    return (f"{BASE}/{directory}", workInfo.get("ocred", ocred))


def getFile(source, ocred):
    """Resolve a work data file location, given by key of directory.

    Parameters
    ----------
    source: string
        Key in the `WORKS` dictionary (*known work)*,
        or directory in the file system (*unknown work*).
    ocred: boolean or None
        Whether the work is in the OCR pipeline.
        For known works this is known, but it can be overriden.
        For unknown works it must be specified, and if not, `True`
        is assumend.

    Returns
    -------
        (string | None, boolean | None)
        If the work is known and exists, or unknown and exists,
        its (tsv) data file is returned.
        If `givenOcr` is `None`, and the work is known, its
        ocr status is returned, otherwise None.
    """

    (workDir, ocred) = getWorkDir(source, ocred)
    if workDir is None:
        return (None, ocred)

    workInfo = WORKS[source]
    sourceInfo = workInfo["source"]

    if "file" not in sourceInfo:
        print(f"{source} does not specify a file in its source")
        return (None, ocred)

    fileName = sourceInfo["file"]

    return (f"{workDir}/{fileName}", ocred)


def getTfDest(source, versionTf):
    """Resolve a work tf directory, given by key of directory.

    Parameters
    ----------
    source: string
        Key in the `WORKS` dictionary (*known work)*,
        or directory in the file system (*unknown work*).
    versionTf: string
        The version of the TF data.
        This directory does not have to exist.

    Returns
    -------
        string | None
        If the work is known and exists, or unknown and exists,
        its versioned tf data directory is returned.
    """

    (workDir, ocred) = getWorkDir(source, None)
    if workDir is None:
        return None
    if versionTf is None:
        print("Missing TF version")
        return None
    workInfo = WORKS[source]
    return f"{BASE}/{workInfo['dest']}/{versionTf}"
