"""Registry of sources.

# Works

The books of the Fusus project are in the directory `ur` of this repo.

There you find subdirectories corresponding to

* **Afifi** The Fusus Al Hikam in the Afifi edition.
* **Lakhnawi** The Fusus Al Hikam in the Lakhnawi edition.
  The source is a textual PDF, not in the online repo, from which
  structured data is derived by means of a specific workflow,
  not the *pipeline*.
* **commentary Xxx** Commentary books

These are the *known* works.
They are registered in `WORKS` and assigned an acronym there.

When new works become available, you can give them an acronym and register them here.

All functions here and in `fusus.convert` make use of this registry,
which makes it possible to refer to known works by acronyms.

The `fusus` package can also work with source material in arbitrary locations.

If you want to process other works, that is still possible,
just provide directories where source acronyms are expected.

As far as the pipeline is concerned, the input of a book is a directory
of page images. More precisely, it is a directory in which there is
a subdirectory `in` having the page images.

When the pipeline runs, it produces additional directories
containing intermediate results and output.

For details, see `fusus.book`, and `fusus.lakhnawi`.

It is assumed that unknown works use the OCR pipeline.
If that is not true, pass a parameter `ocred=False` to the function,
or, on the command line, pass `noocr`.
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
    fususlur=dict(
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
        dest="tf/Lakhnawi",
        toc=True,
        ocred=False,
        sep="\t",
    ),
    fususaur=dict(
        meta=dict(
            name="fusus",
            title="Fusus Al Hikam",
            author="Ibn Arabi",
            editor="Afifi",
            published="pdf, personal communication",
            period="1165-1240",
        ),
        source=dict(
            dir="ur/Afifi",
            file="allpages.tsv",
        ),
        dest="tf/Afifi",
        toc=False,
        ocred=True,
        sep="\t",
    ),
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
            dir="fusust-text-laboratory",
            file="fusus.csv",
        ),
        sourceToc=dict(
            dir="ur/Lakhnawi",
            file="allpages.tsv",
            sep="\t",
        ),
        dest="tf/Lakhnawi",
        toc=True,
        ocred=False,
        sep=",",
        extra=True,
        skipcol=11,
    ),
    fusus=dict(
        meta=dict(
            name="fusus",
            title="Fusus Al Hikam",
            author="Ibn Arabi",
            editor="Lakhnawi and Afifi (merged with diff info)",
            published="pdf, personal communication",
            period="1165-1240",
        ),
        source=dict(
            dir="ur/Fusus",
            file="LFmergedAF.tsv",
        ),
        sourceToc=dict(
            dir="ur/Lakhnawi",
            file="allpages.tsv",
            sep="\t",
        ),
        dest="tf/Fusus",
        toc=True,
        ocred=False,
        sep=",",
        extra=True,
        skipcol=11,
        merged=True,
    ),
    fususa=dict(
        meta=dict(
            name="fusus",
            title="Fusus Al Hikam",
            author="Ibn Arabi",
            editor="Afifi",
            published="pdf, personal communication",
            period="1165-1240",
        ),
        source=dict(
            dir="fusust-text-laboratory",
            file="AfifiTweaked.csv",
        ),
        dest="tf/Afifi",
        toc=False,
        ocred=True,
        sep=",",
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
    The Afifi page images are in the `in` subdirectory of its work
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
        source = os.path.expanduser(source)
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

    workInfo = WORKS.get(source, None)
    if workInfo is None:
        return (workDir, ocred)

    if "source" not in workInfo:
        print(f"{source} does not specify a source")
        return (workDir, ocred)

    sourceInfo = workInfo["source"]

    if "file" not in sourceInfo:
        print(f"{source} does not specify a file in its source")
        return (workDir, ocred)

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
