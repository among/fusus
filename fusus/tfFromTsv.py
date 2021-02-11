"""Convert TSV data to Text-Fabric.

The TSV data consists of one-word-per-line files for each page,
and for each word the line specifies its text, its bounding boxes in the original,
and its containing spaces on the page (line, block, etc).

The TSV data from OCRed pages is slightly different from that of the
textual extraction of the Lakhnawi PDF, but they share most fields.

The code here can deal with both kinds of input.

See also

* `fusus.convert`
* [Text-Fabric](https://annotation.github.io/text-fabric/tf/index.html)
"""

import collections
import re

from tf.fabric import Fabric
from tf.convert.walker import CV
from tf.writing.transcription import Transcription as Tr

from .char import UChar
from .works import WORKS, getFile, getTfDest
from .lib import parseNums


EXT = ".tsv"
VERSION_TF = None

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


otext = {}
otext[None] = {
    "fmt:text-orig-full": "{pre}{text}{post}",
    "fmt:text-orig-plain": "{prea}{plain}{posta}",
    "fmt:text-orig-nice": "{prea}{nice}{posta}",
    "fmt:text-orig-trans": "{prea}{trans}{posta}",
}
otext[False] = {
    "sectionFeatures": "n,n,ln",
    "sectionTypes": "piece,page,line",
}
otext[True] = {
    "sectionFeatures": "n,b,ln",
    "sectionTypes": "page,block,line",
}

intFeatures = {}
intFeatures[None] = set(
    """
        n
        ln
    """.strip().split()
)
intFeatures[False] = {"np"}
intFeatures[True] = set()

featureMeta = {}

featureMeta[None] = {
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
    "nice": {
        "description": "text string of a word in latin transcription (beta code)",
        "format": "string, latin with diacritics",
    },
    "plain": {
        "description": "text string of a word in ascii transcription (beta code)",
        "format": "string, ascii",
    },
    "post": {
        "description": "punctuation and/or space immediately after a word",
        "format": "string",
    },
    "posta": {
        "description": "punctuation and/or space immediately after a word",
        "format": "string, ascii",
    },
    "pre": {
        "description": "punctuation (but no whitespace) immediately before a word",
        "format": "string",
    },
    "prea": {
        "description": "punctuation (but no whitespace) immediately before a word",
        "format": "string, ascii",
    },
    "text": {
        "description": "text string of a word without punctuation",
        "format": "string",
    },
    "trans": {
        "description": (
            "text string of a word in romanized transcription" " (Library of Congress)"
        ),
        "format": "string, latin with diacritics",
    },
}

featureMeta[False] = {
    "dir": {
        "description": "writing direction of a span",
        "format": "string, either r or l",
    },
    "ln": {
        "description": "sequence number of a line within a page",
        "format": "number",
    },
    "n": {
        "description": (
            "sequence number of a piece, page, column within a line, or span"
        ),
        "format": "number",
    },
    "np": {
        "description": "sequence number of a proper content piece",
        "format": "number",
    },
    "title": {
        "description": "title of a piece",
        "format": "string",
    },
}

featureMeta[True] = {
    "b": {
        "description": "name of a block inside a stripe",
        "format": "string, either r or l",
    },
    "confidence": {
        "description": "confidence of OCR recognition of the word",
        "format": "number between 0 and 100 (including)",
    },
    "n": {
        "description": "sequence number of a piece, page, or stripe",
        "format": "number",
    },
    "ln": {
        "description": "sequence number of a line within a block",
        "format": "number",
    },
}

# DISTILL TABLE of CONTENTS

TOC_PAGES = (4, 5)

TOC_LINE_RE = re.compile(
    r"""
    ^
    ([٠-٩]+)
    ‐
    ([^…]+)
    …+
    ([٠-٩]+)
    $
""",
    re.X,
)

PIECE_RE = re.compile(
    r"""
    ^
    \[
    ([٠-٩]+)
    \]
    (.*)
    $
""",
    re.X,
)


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

pageNums = None


TYPE_MAPS = {
    False: ["page", "line", "column", "span"],
    True: ["page", "stripe", "block", "line"],
}


def convert(source, ocred, pages, versionTf):
    global pageNums
    global SRC_FILE
    global TYPE_MAP
    global HAS_TOC
    global OCRED
    global U
    global VERSION_TF

    U = UChar()

    pageNums = parseNums(pages)

    workInfo = WORKS[source]
    dest = getTfDest(source, versionTf)
    (SRC_FILE, OCRED) = getFile(source, ocred)
    HAS_TOC = workInfo.get("toc", False)
    TYPE_MAP = TYPE_MAPS[OCRED]
    VERSION_TF = versionTf

    cv = CV(Fabric(locations=dest))

    return cv.walk(
        director,
        slotType,
        otext=otext[None] | otext[OCRED],
        generic=generic(source),
        intFeatures=intFeatures[None] | intFeatures[OCRED],
        featureMeta=featureMeta[None] | featureMeta[OCRED],
        generateTf=True,
    )


# DIRECTOR


def director(cv):
    """Read tsv data fields.

    Fields are integer valued, except for fields with names ending in $.

    If a row comes from the result of OCR we have the fields:

    ```
    stripe block$ line left top right bottom confidence text$
    ```

    We prepend the page number in this case, yielding

    ```
    page stripe block$ line left top right bottom confidence text$
    ```

    Otherwise we have:

    ```
    page line column span direction$ left top right bottom text$
    ```

    See `fusus.lakhnawi.Lakhnawi.tsvPages`.

    The block in an OCRed file is either `r` or `l` or nothing, it corresponds
    to material to the left and right of a vertical stroke.
    If there is no vertical stroke, there is just one block.

    The column in a non OCRed file is either `1` or `2` and comes
    from a line partitioned into two regions by means of white space.

    In both cases, the first 4 fields denote a sectional division in
    the words.
    """

    stops = U.stops
    nonLetter = U.nonLetter
    nonLetterRange = re.escape("".join(sorted(nonLetter)))

    WORD_RE = re.compile(
        fr"""
        (
            [^{nonLetterRange}]+
        )
        |
        (
            [{nonLetterRange}]+
        )
""",
        re.X,
    )
    errors = collections.defaultdict(set)

    cur = [None, None, None, None]
    prev = [None, None, None, None]
    nSec = len(prev)

    data = []

    with open(SRC_FILE) as fh:
        next(fh)
        for line in fh:
            row = tuple(line.rstrip("\n").split("\t"))
            page = int(row[0])
            if pageNums is not None and page not in pageNums:
                continue

            if OCRED:
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

    boxL = nSec if OCRED else nSec + 1

    if HAS_TOC:
        toc = getToc(data)
        curPiece = cv.node("piece")
        cv.feature(curPiece, n=1, title="front")

    curSentence = cv.node("sentence")
    nSentence = 1
    cv.feature(curSentence, n=nSentence)

    for (r, fields) in enumerate(data):
        if HAS_TOC:
            page = fields[0]
            if page in toc and page != prev[0]:
                for i in reversed(range(nSec)):
                    cv.terminate(cur[i])

                cv.terminate(curSentence)
                cv.terminate(curPiece)
                nSentence = 1
                curSentence = cv.node("sentence")
                cv.feature(curSentence, n=nSentence)

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
                    if OCRED and j == 2:
                        cv.feature(cn, b=fields[j])
                    elif OCRED and j == 3 or not OCRED and j == 1:
                        cv.feature(cn, ln=fields[j])
                    else:
                        cv.feature(cn, n=fields[j])
                    if not OCRED and j == nSec - 1:
                        cv.feature(cn, dir=fields[nSec])
                break
        for i in range(nSec):
            prev[i] = fields[i]

        string = fields[-1]
        parts = []
        first = True
        firstNonLetters = False

        for (letters, nonLetters) in WORD_RE.findall(string):
            if first:
                if nonLetters:
                    parts.append([nonLetters, "", ""])
                    firstNonLetters = True
                else:
                    parts.append(["", letters, ""])
                first = False
            elif firstNonLetters:
                parts[-1][1] = letters
                firstNonLetters = False
            elif letters:
                parts.append(["", letters, ""])
            else:
                parts[-1][-1] = nonLetters
        if parts:
            parts[-1][-1] += " "

        for (pre, text, post) in parts:
            textp = Tr.asciiFromArabic(text)
            textn = Tr.latinFromArabic(text)
            textt = Tr.standardFromArabic(text)
            s = cv.slot()
            cv.feature(
                s,
                boxl=fields[boxL],
                boxt=fields[boxL + 1],
                boxr=fields[boxL + 2],
                boxb=fields[boxL + 3],
                text=text,
                plain=textp,
                nice=textn,
                trans=textt,
            )
            if pre:
                prea = Tr.asciiFromArabic(pre)
                cv.feature(s, pre=pre, prea=prea)
            if post:
                posta = Tr.asciiFromArabic(post)
                cv.feature(s, post=post, posta=posta)
                if any(c in stops for c in post):
                    cv.terminate(curSentence)
                    curSentence = cv.node("sentence")
                    nSentence += 1
                    cv.feature(curSentence, n=nSentence)
            if OCRED:
                cv.feature(s, confidence=fields[-2])

    cv.terminate(curSentence)

    for i in reversed(range(nSec)):
        if cur[i]:
            cv.terminate(cur[i])

    if HAS_TOC:
        cv.terminate(curPiece)

    for feat in featureMeta:
        if not cv.occurs(feat):
            cv.meta(feat)

    if errors:
        for kind in sorted(errors):
            instances = sorted(errors[kind])
            nInstances = len(instances)
            showInstances = instances[0:20]
            print(f"ERROR {kind}: {nInstances} x")
            print(", ".join(showInstances))


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
