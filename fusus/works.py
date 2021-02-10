import os


BASE = os.path.expanduser("~/github/among/fusus")

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

They are given a keyword, and under that keyword
there is metadata, the source directory, the destination directory for
Text-Fabric files, whether the work has a table of contents, and whether
the work is the outcome of an OCR process.

Functions that deal with works can be given the keyword as an argument,
and then they know how to deal with its data.
"""


def getFile(source):
    if source not in WORKS:
        print(f"Unknown work `{source}`")
        return None

    workInfo = WORKS[source]

    if "source" not in workInfo:
        print(f"{source} does not specify a source")
        return None

    sourceInfo = workInfo["source"]

    if "dir" not in sourceInfo:
        print(f"{source} does not specify a directory in its source")
        return None
    if "file" not in sourceInfo:
        print(f"{source} does not specify a file in its source")
        return None
    directory = sourceInfo["dir"]
    fileName = sourceInfo["file"]

    srcDir = f"{BASE}/{directory}"

    return f"{srcDir}/{fileName}"


def getDest(source, versionTf):
    workInfo = WORKS[source]
    return f"{BASE}/{workInfo['dest']}/{versionTf}"
