"""Convenience methods to call conversions to and from tsv and to tf.

The pipeline can read Arabic books in the form of page images,
and returns structured data in the form of tab separated files.

# Books

As far as the pipeline is concerned, the input of a book is a directory
of page images. More precisely, it is a directory in which there is
a subdirectory `in` having the page images.

The books of the Fusus project are in the directory `ur` of this repo.

There you find subdirectories corresponding to

* **Affifi** The Fusus Al Hikam in the Affifi edition.
* **Lakhnawi** The Fusus Al Hikam in the Lakhnawi edition.
  The source is a textual PDF, not in the online repo, from which
  structured data is derived by means of a specific workflow,
  not the *pipeline*.
* **commentary Xxx** Commentary books

When the pipeline runs, it produces additional directories
containing intermediate results and output.

For details, see `fusus.works`, `fusus.book`, and `fusus.lakhnawi`.

All functions here make use of `fusus.works`, which makes it possible to
refer to known works by keywords.

If you want to process other works, that is still possible,
just provide directories where source keywords are expected.

It is assumed that unknown works use the OCR pipeline.
If that is not true, pass a parameter `ocred=False` to the function,
or, on the command line, pass `noocr`.

## Run

You can run the pipeline on the known works inside the *ur* directory in this repo or
on books that you provide yourself.

This script supports one-liners on the command line
to execute the pipeline and various conversion processes.

See  `fusus.convert.HELP`.

## Load TSV

The function `loadTsv` to load TSV data in memory.
For known works, it will also convert the data types of the appropriate fields
to integer.

"""

import sys
import re

from tf.core.helpers import unexpanduser

from .works import getFile, getWorkDir, getTfDest
from .lib import parseNums
from .book import Book
from .lakhnawi import Lakhnawi
from .tfFromTsv import convert, loadTf


__pdoc__ = {}

HELP = """
Convert tsv data files to TF and optionally loads the TF.

python3 -m fusus.convert --help
python3 -m fusus.convert tsv source ocr|noocr pages
python3 -m fusus.convert tf source ocr|noocr pages versiontf [load] [loadonly]

--help: print this text and exit

"source"  : a work (given as keyword or as path to its work directory)
            Examples:
                fususl (Fusus Al Hikam in Lakhnawi edition)
                fususa (Fusus Al Hikam in Affifi edition)
                any commentary by its keyword
                ~/github/myorg/myrepo/mydata
                mydir/mysubdir
"pages"   : page specification, only process these pages; default: all pages
            Examples:
                50
                50,70
                50-70,91,92,300-350
"ocr"     : assume the work is in the OCR pipeline
"noocr"   : assume the work is not in the OCR pipeline
            (it is then a text extract from a pdf)

For tf only:

"load"    : loads the generated TF; if missing this step is not performed
"loadOnly": does not generate TF; loads previously generated TF
"""
"""Help"""

__pdoc__["HELP"] = f"``` text\n{HELP}\n```"


def makeTf(
    versionTf=None,
    source=None,
    ocred=None,
    pages=None,
    load=False,
    loadOnly=False,
):
    """Make Text-Fabric data out of the TSV data of a work.

    The work is specified either by the name of a known work
    (e.g. `fususa`, `fususl`)
    or by specifying the work directory.

    The function needs to know whether the tsv comes out of an OCR process or
    from the text extraction of a PDF.

    In case of a known work, this is known and does not have to be specified.
    Otherwise you have to pass it.

    Parameters
    ----------
    versionTf: string
        A version number for the TF to be generated, e.g. `0.3`.
        Have a look in the fusus tf subdirectory, and see which version already exists,
        and then choose a higher version if you do not want to overwrite the existing
        version.
    source: string, optional `None`
        The key of a known work, see `fusus.works.WORKS`.
        Or else the path to directory of the work.
    ocred: string
        Whether the tsv is made by the OCR pipeline.
        Not needed in case of a known work.
    pages: string|int, optional `None`
        A specification of zero or more page numbers (see `fusus.lib.parseNums`).
        Only rows belonging to selected pages will be extracted.
        If None, all pages will be taken.
    load: boolean, optional `False`
        If TF generation has succeeded, load the tf files for the first time.
        This will trigger a one-time precomputation step.
    loadOnly: boolean, optional `False`
        Skip TF generation, assume the TF is already in place, and load it.
        This might trigger a one-time precomputation step.

    Returns
    -------
    nothing
        It will run the appripriate pipeline and generate tf in the appropriate
        locations.
    """

    doLoad = load or loadOnly
    doConvert = not loadOnly

    print("TSV to TF converter for the Fusus project")
    print(f"TF  target version = {versionTf}")

    good = True

    print(f"===== SOURCE {source} =====")

    if doConvert:
        if not convert(source, ocred, pages, versionTf):
            good = False

    if good:
        if doLoad:
            dest = getTfDest(source, versionTf)
            if dest is None:
                good = False
            else:
                loadTf(dest)

    return good


def makeTsv(source=None, ocred=None, pages=None):
    """Make TSV data out of the source of a work.

    The work is specified either by the name of a known work
    (e.g. `fususa`, `fususl`)
    or by specifying the work directory.

    The function needs to know whether the tsv comes out of an OCR process or
    from the text extraction of a PDF.

    In case of a known work, this is known and does not have to be specified.
    Otherwise you have to pass it.

    Parameters
    ----------
    source: string, optional `None`
        The key of a known work, see `fusus.works.WORKS`.
        Or the path to directory of the work.
    ocred: string
        Whether the tsv is made by the OCR pipeline.
        Not needed in case of a known work.
    pages: string|int, optional `None`
        A specification of zero or more page numbers (see `fusus.lib.parseNums`).
        Only rows belonging to selected pages will be extracted.
        If None, all pages will be taken.

    Returns
    -------
    nothing
        It will run the appripriate pipeline and generate tsv in the appropriate
        locations.
    """

    (workDir, ocred) = getWorkDir(source, ocred)
    if workDir is None:
        return

    ocrRep = "with OCR" if ocred else "no OCR"

    print(f"Making TSV data from {unexpanduser(workDir)} ({ocrRep})")

    if ocred:
        B = Book(cd=workDir)
        B.process(pages=pages)
        B.exportTsv(pages=pages)
    else:
        Lw = Lakhnawi()

        print("Reading PDF")
        Lw.getPages(pages)

        print("\nExporting TSV")
        Lw.tsvPages(pages)

        print("Closing")
        Lw.close()


def loadTsv(source=None, ocred=None, pages=None):
    """Load a tsv file into memory.

    The tsv file either comes from a known work or is specified by a path.

    If it comes from a known work, you only have to pass the key of that work,
    e.g. `fususa`, or `fususl`.

    The function needs to know whether the tsv comes out of an OCR process or
    from the text extraction of a PDF.

    In case of a known work, this is known and does not have to be specified.
    Otherwise you have to pass it.

    Parameters
    ----------
    source: string, optional `None`
        The key of a known work, see `fusus.works.WORKS`.
        Or the path to the tsv file.
    ocred: string
        Whether the tsv file comes from the OCR pipeline.
        Not needed in case of a known work.
    pages: string|int, optional `None`
        A specification of zero or more page numbers (see `fusus.lib.parseNums`).
        Only rows belonging to selected pages will be extracted.
        If None, all pages will be taken.

    Returns
    -------
    tuple
        Two members:

        * head: a tuple of field names
        * rows: a tuple of data rows, where each row is a tuple of its fields
    """

    (sourceFile, ocred) = getFile(source, ocred)
    if sourceFile is None:
        return ((), ())

    pageNums = parseNums(pages)

    data = []

    print(f"Loading TSV data from {unexpanduser(sourceFile)}")
    with open(sourceFile) as fh:
        head = tuple(next(fh).rstrip("\n").split("\t"))

        for line in fh:
            row = tuple(line.rstrip("\n").split("\t"))
            page = int(row[0])
            if pageNums is not None and page not in pages:
                continue

            if ocred:
                row = (
                    page,
                    int(row[1]),
                    row[2],
                    int(row[3]),
                    *(None if c == "?" else int(c) for c in row[4:8]),
                    int(row[8]),
                    row[9],
                )
            else:
                row = (
                    page,
                    *(int(c) for c in row[1:4]),
                    row[4],
                    *(None if c == "?" else int(c) for c in row[5:9]),
                    row[9],
                )

            data.append(row)

    return (head, tuple(data))


# MAIN


def parseArgs(args):
    """Parse arguments from the command line.

    Performs sanity checks.

    Parameters
    ----------
    args: list
        All command line arguments.
        The full command is stripped from what `sys.argv` yields.

    Returns
    -------
    passed: dict
        The interpreted values of the command line arguments,
        which will be passed on to the rest of program.
    """

    passed = dict(
        command=None,
        source=None,
        ocred=None,
        pages=None,
        load=None,
        loadOnly=None,
        versionTf=None,
    )
    good = True

    NUMS = re.compile(r"^[0-9][0-9,-]*$")

    def setArg(name, value):
        nonlocal good

        if passed[name] is None:
            passed[name] = value
        else:
            print(f"Repeated: `{value}` for {name}")
            good = False

    for arg in args:
        if arg in {"tf", "tsv"}:
            setArg("command", arg)
        elif arg == "load":
            setArg("load", True)
        elif arg == "loadonly":
            setArg("loadOnly", True)
        elif arg == "ocr":
            setArg("ocred", True)
        elif arg == "noocr":
            setArg("ocred", False)
        elif "." in arg:
            setArg("versionTf", arg)
        elif NUMS.match(arg):
            setArg("pages", arg)
        elif arg == "--help":
            print(HELP)
            good = None
        else:
            setArg("source", arg)

    if good:
        if passed["command"] is None:
            print("No command specified (tf or tsv)")
            good = False
        if passed["source"] is None:
            print(
                "No source specified (fususl, fususa, commentary_name, directory_path)"
            )
            good = False
        if passed["command"] == "tf":
            if passed["versionTf"] is None:
                print("No TF version specified (e.g. 0.3)")
                good = False
            if passed["load"] is None:
                passed["load"] = False
            if passed["loadOnly"] is None:
                passed["loadOnly"] = False
        else:
            for name in ("versionTf", "load", "loadOnly"):
                if passed[name] is not None:
                    print(f"Illegal argument `{passed[name]}` for {name}")
                    good = False
                del passed[name]

    return (good, passed)


def main():
    """Perform tasks.

    See `HELP`.
    """

    args = () if len(sys.argv) == 1 else tuple(sys.argv[1:])
    (good, passed) = parseArgs(args)
    if not good:
        return good is None

    kwargs = {k: v for (k, v) in passed.items() if k != "command"}

    if passed["command"] == "tsv":
        print("TSV to TF converter for the Fusus project")
        return makeTsv(**kwargs)
    elif passed["command"] == "tf":
        print(f"TF  target version = {passed['versionTf']}")
        return makeTf(**kwargs)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
