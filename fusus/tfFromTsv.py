import os
import sys
import collections
import re

from tf.fabric import Fabric
from tf.convert.walker import CV


HELP = """

Convert tsv data files to TF and optionally loads the TF.

python3 tfFromTsv.py source+ ["load"] ["loadonly"] [page] [--help]

--help: print this text and exit

"source+" : one or more sources (given as keyword) to convert to TF
"load"    : loads the generated TF; if missing this step is not performed
"loadOnly": does not generate TF; loads previously generated TF
page      : only process this page; default: all pages
"""


EXT = ".tsv"
VERSION_TF = 0.1

BASE = os.path.expanduser("~/github/among/fusus")

WORKS = dict(
    fususl=dict(
        meta=dict(
            name="fusus",
            title="Fusus Al Hikram",
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
    ),
    fususa=dict(
        meta=dict(
            name="fusus",
            title="Fusus Al Hikram",
            author="Ibn Arabi",
            editor="Affifi",
            published="pdf, personal communication",
            period="1165-1240",
        ),
        source=dict(
            dir="ur/Affifi1/out",
        ),
        dest="tf/fusus/Lakhnawi",
    ),
)


# TF CONFIGURATION

slotType = "word"

GENERIC = dict(
    language="ara",
    institute="Univ Utrecht NL/DANS",
    project="Fusus",
    researcher="Cornelis van Lit",
    converters="Cornelis van Lit, Dirk Roorda (Text-Fabric)",
    sourceFormat="CSV (tab-separated)",
)


def generic(source):
    return {**GENERIC, **WORKS[source]["meta"]}


otext = {
    "fmt:text-orig-full": "{text}{punc}",
    # "fmt:text-orig-trans": "{trans}{punc}",
    "sectionFeatures": "title,n,n",
    "sectionTypes": "piece,page,line",
}

intFeatures = set(
    """
        n
        np
    """.strip().split()
)

featureMeta = {
    "boxl": {
        "description": "left x-coordinate of word",
        "format": "number",
    },
    "boxt": {
        "description": "top y-coordinate of word",
        "format": "number",
    },
    "boxr": {
        "description": "right x-coordinate of word",
        "format": "number",
    },
    "boxb": {
        "description": "bottom y-coordinate of word",
        "format": "number",
    },
    "confidence": {
        "description": "confidence of OCR recognition of the word",
        "format": "number between 0 and 100 (including)",
    },
    "dir": {
        "description": "writing direction of a span",
        "format": "string, either r or l",
    },
    "n": {
        "description": (
            "sequence number of a piece, page, line within a page,"
            " column within a line, or span within a column"
        ),
        "format": "number",
    },
    "np": {
        "description": "sequence number of a proper content piece",
        "format": "number",
    },
    "name": {
        "description": "name of a column in ocred output",
        "format": "string, either r or l",
    },
    "punc": {
        "description": "punctuation behind a word",
        "format": "string",
    },
    "text": {
        "description": "text string of a word without punctuation",
        "format": "string",
    },
    "title": {
        "description": "title of a piece",
        "format": "string",
    },
    "trans": {
        "description": "transliterated text string of a word without punctuation",
        "format": "string",
    },
}


# ERROR HANDLING


def docSummary(occs):
    nOccs = len(occs)
    rep = "   0x" if not nOccs else f"   1x {occs[0]}" if nOccs == 1 else ""
    if not rep:
        examples = " ".join(occs[0:2])
        rest = " ..." if nOccs > 2 else ""
        rep = f"{nOccs:>4}x {examples}{rest}"
    return f"{rep:<30}"


def showDiags(diags, kind, batch=20):
    if not diags:
        print("No diags")
    else:
        for (diag, docs) in sorted(diags.items()):
            docRep = docSummary(sorted(docs))
            print(f"{kind} {diag} {len(docs):>4}x {docRep}")


# DISTILL TABLE of CONTENTS

TOC_PAGES = (4, 5)

TOC_LINE_RE = re.compile(r"""
    ^
    ([٠-٩]+)
    ‐
    ([^…]+)
    …+
    ([٠-٩]+)
    $
""", re.X)

PIECE_RE = re.compile(r"""
    ^
    \[
    ([٠-٩]+)
    \]
    (.*)
    $
""", re.X)


def getToc(data):
    (start, end) = TOC_PAGES

    lines = []
    curLine = []

    prevLine = None

    for fields in data:
        page = fields[0]
        if page < start:
            continue
        if page > end:
            break

        line = fields[1]
        if prevLine is None or prevLine != line:
            if curLine:
                lines.append("".join(curLine))
                curLine = []
            space = ""

        curLine.append(f"{space}{fields[-1]}")
        prevLine = line

    if curLine:
        lines.append("".join(curLine))

    toc = {}

    for line in lines:
        match = TOC_LINE_RE.match(line)
        if not match:
            continue
        (seq, title, pg) = match.group(1, 2, 3)
        seq = int(seq[::-1])
        pg = int(pg[::-1])
        pSeq = None
        matchP = PIECE_RE.match(title)
        if matchP:
            (pSeq, title) = matchP.group(1, 2)
            pSeq = int(pSeq[::-1])
        toc[pg] = (seq, pSeq, title)
    return toc


# SET UP CONVERSION

givenPage = None


def getFiles(source):
    workInfo = WORKS[source]

    sourceInfo = workInfo["source"]
    directory = sourceInfo["dir"]
    fileName = sourceInfo.get("file", None)

    srcDir = f"{BASE}/{directory}"

    if fileName:
        return [(None, f"{srcDir}/{fileName}")]

    files = []
    with os.scandir(srcDir) as dh:
        for entry in dh:
            if entry.is_file():
                fileName = entry.name
                if not fileName.endswith(EXT):
                    continue
                page = fileName.removesuffix(EXT).lstrip("0")
                if not page.isdigit():
                    print(f"skipping {fileName}")
                    continue

                page = int(page)
                if givenPage is not None and page != givenPage:
                    continue

                files.append((page, f"{srcDir}/{fileName}"))
    return sorted(files)


TYPE_MAPS = {
    True: ["page", "line", "column", "span"],
    False: ["page", "stripe", "column", "line"],
}


def convert(source, page):
    global givenPage
    global SRC_FILES
    global TYPE_MAP
    global HAS_TOC

    givenPage = page

    workInfo = WORKS[source]
    dest = f"{BASE}/{workInfo['dest']}/{VERSION_TF}"
    SRC_FILES = getFiles(source)
    HAS_TOC = workInfo.get("toc", False)
    TYPE_MAP = TYPE_MAPS[HAS_TOC]

    cv = CV(Fabric(locations=dest))

    return cv.walk(
        director,
        slotType,
        otext=otext,
        generic=generic(source),
        intFeatures=intFeatures,
        featureMeta=featureMeta,
        generateTf=True,
    )


# DIRECTOR


warnings = collections.defaultdict(set)
errors = collections.defaultdict(set)


def director(cv):
    """Read tsv data fields.

    Fields are integer valued, except for fields with names ending in $.

    If a row comes from the result of OCR we have the fields:

    ```
    stripe column$ line left top right bottom confidence text$
    ```

    We prepend the page number in this case, yielding

    ```
    page stripe column$ line left top right bottom confidence text$
    ```

    Otherwise we have:

    page line column span direction$ left top right bottom text$

    The column in an OCRed file is either `r` or `l`, it corresponds
    to material to the left and right of a vertical stroke.

    The column in a non OCRed file is either `1` or `2` and comes
    from a line partitioned into two regions by means of white space.

    In both cases, the first 4 fields denote a sectional division in
    the words.
    """

    cur = [None, None, None, None]
    prev = [None, None, None, None]
    nSec = len(prev)

    ocred = True
    data = []

    for (page, path) in SRC_FILES:
        if page is None:
            ocred = False
        with open(path) as fh:
            next(fh)
            for line in fh:
                row = tuple(line.rstrip("\n").split("\t"))
                if ocred:
                    row = (page,) + (
                        int(row[0]),
                        row[1],
                        int(row[2]),
                        *(None if c == "?" else int(c) for c in row[3:7]),
                        int(row[7]),
                        row[8],
                    )
                    data.append(row)
                else:
                    page = int(row[0])
                    if givenPage is not None and page != givenPage:
                        continue
                    row = (
                        *(int(c) for c in row[0:4]),
                        row[4],
                        *(None if c == "?" else int(c) for c in row[5:9]),
                        row[9],
                    )
                    data.append(row)

    boxL = nSec if ocred else nSec + 1

    if HAS_TOC:
        toc = getToc(data)
        curPiece = cv.node("piece")
        cv.feature(curPiece, n=1, title="front")

    for fields in data:
        if HAS_TOC:
            page = fields[0]
            if page in toc and page != prev[0]:
                for i in reversed(range(nSec)):
                    cv.terminate(cur[i])

                cv.terminate(curPiece)

                (n, np, title) = toc[page]
                curPiece = cv.node("piece")
                cv.feature(curPiece, n=n, title=title)
                if np is not None:
                    cv.feature(curPiece, np=np)

        for i in range(nSec):
            if fields[i] != prev[i]:
                for j in reversed(range(i, nSec)):
                    cv.terminate(cur[j])
                for j in range(i, nSec):
                    cn = cv.node(TYPE_MAP[j])
                    cur[j] = cn
                    if ocred and j == 2:
                        cv.feature(cn, name=fields[j])
                    else:
                        cv.feature(cn, n=fields[j])
                    if not ocred and j == nSec - 1:
                        cv.feature(cn, dir=fields[nSec])
                break
        for i in range(nSec):
            prev[i] = fields[i]

        s = cv.slot()
        cv.feature(
            s,
            boxl=fields[boxL],
            boxt=fields[boxL + 1],
            boxr=fields[boxL + 2],
            boxb=fields[boxL + 3],
            text=fields[-1],
            punc=" ",
        )
        if ocred:
            cv.feature(s, confidence=fields[-2])

    for i in reversed(range(nSec)):
        if cur[i]:
            cv.terminate(cur[i])

    if HAS_TOC:
        cv.terminate(curPiece)

    for feat in featureMeta:
        if not cv.occurs(feat):
            cv.meta(feat)


# TF LOADING (to test the generated TF)


def loadTf(outDir):
    TF = Fabric(locations=[outDir])
    allFeatures = TF.explore(silent=True, show=True)
    loadableFeatures = allFeatures["nodes"] + allFeatures["edges"]
    api = TF.load(loadableFeatures, silent=False)
    if api:
        print(f"max node = {api.F.otype.maxNode}")
        print("Frequencies of words")
        for (word, n) in api.F.text.freqList()[0:20]:
            print(f"{n:>6} x {word}")


# MAIN


def parseArgs(args):
    page = None
    sources = []
    good = True
    flags = {}

    for arg in args:
        if arg in {"load", "loadonly"}:
            flags[arg] = True
        elif arg == "--help":
            print(HELP)
            good = None
        elif arg.isdigit() or "-" in arg:
            if "-" in arg:
                (b, e) = arg.split("-", 1)
                if b.isdigit() and e.isdigit():
                    values = set(range(int(b), int(e) + 1))
                else:
                    print(f"Unrecognized argument `{arg}`")
                    good = False
                    continue
            else:
                values = {int(arg)}
            if page is None:
                page = values
            else:
                print(f"Repeated pages argument `{arg}`")
                good = False
                continue
        else:
            kv = arg.split("=", 1)
            if len(kv) == 1:
                sources.append(arg)
            else:
                (k, v) = kv
                flags[k] = v

    if len(sources) == 0:
        print("No source specified")
        good = False

    return (good, sources, page, flags)


def main():
    args = () if len(sys.argv) == 1 else tuple(sys.argv[1:])
    (good, sources, page, flags) = parseArgs(args)
    if not good:
        return good is None

    doLoad = flags.get("load", False) or flags.get("loadonly", False)
    doConvert = not flags.get("loadonly", False)

    print("TSV to TF converter for the Fusus project")
    print(f"TF  target version = {VERSION_TF}")

    good = True

    for source in sources:
        print(f"===== SOURCE {source} =====")

        thisGood = True

        if doConvert:
            if not convert(source, page):
                thisGood = False

        if thisGood:
            if doLoad:
                workInfo = WORKS[source]
                dest = f"{BASE}/{workInfo['dest']}/{VERSION_TF}"
                loadTf(dest)

        if not thisGood:
            good = False

    return good


sys.exit(0 if main() else 1)
