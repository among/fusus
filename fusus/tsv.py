import os
from tf.core.helpers import unexpanduser

from .works import WORKS, getFile
from .lib import parseNums


def loadTsv(source=None, path=None, ocred=None, pages=None):
    """Load a tsv file into memory.

    The tsv file either comes from a known work or is specified by a path.

    If it comes from a known work, you only hace to pass the key of that work,
    e.g. `fususa`, or `fususl`.

    The function needs to know whether the tsv comes out of an OCR process or
    from the text extraction of a PDF.

    In case of a known work, this is known and does not have to be specified.
    Otherwise you have to pass it.

    Parameters
    ----------
    source: string, optional `None`
        The key of a known work, see `fusus.works.WORKS`.
    path: string
        The path to the tsv file.
        Not needed in case of a known work.
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

    if source is not None and source not in WORKS:
        print(f"Unknown work `{source}`")
        return None

    if path is not None:
        path = os.path.expanduser(path)
    sourceFile = getFile(source) if path is None and source is not None else path
    if sourceFile is None:
        print("Specify a valid `source` or give a `path`")
        return ((), ())
    if not os.path.exists(sourceFile):
        print(f"Source file `{unexpanduser(sourceFile)}` does not exist.")
        return ((), ())

    pageNums = parseNums(pages)
    if source is None:
        isOcred = True if ocred is None else ocred
    else:
        workInfo = WORKS[source]
        isOcred = workInfo.get("ocred", False)

    data = []

    print(f"Loading TSV data from {unexpanduser(sourceFile)}")
    with open(sourceFile) as fh:
        head = tuple(next(fh).rstrip("\n").split("\t"))

        for line in fh:
            row = tuple(line.rstrip("\n").split("\t"))
            page = int(row[0])
            if pageNums is not None and page not in pages:
                continue

            if isOcred:
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
