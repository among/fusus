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
    "fmt:text-orig-full": "{letters}{punc}",
    "fmt:text-orig-plain": "{lettersp}{punca}",
    "fmt:text-orig-nice": "{lettersn}{punca}",
    "fmt:text-orig-trans": "{letterst}{punca}",
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
intFeatures["extra"] = {"poetryverse", "fass"}

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
    "letters": {
        "description": "text string of a word without punctuation",
        "format": "string",
    },
    "lettersn": {
        "description": "text string of a word in latin transcription (beta code)",
        "format": "string, latin with diacritics",
    },
    "lettersp": {
        "description": "text string of a word in ascii transcription (beta code)",
        "format": "string, ascii",
    },
    "letterst": {
        "description": (
            "text string of a word in romanized transcription" " (Library of Congress)"
        ),
        "format": "string, latin with diacritics",
    },
    "punc": {
        "description": "punctuation and/or space immediately after a word",
        "format": "string",
    },
    "punca": {
        "description": "punctuation and/or space immediately after a word",
        "format": "string, ascii",
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

featureMeta["extra"] = {
    "raw": {
        "description": "letters of the word straight from the pdf",
        "format": "string",
    },
    "puncb": {
        "description": "punctuation immediately before a word",
        "format": "string",
    },
    "puncba": {
        "description": "punctuation immediately before a word",
        "format": "string, ascii",
    },
    "qunawims": {
        "description": (
            "on which folio of the oldest manuscript, "
            "penned by Qunawi himself, is this word attested?"
        ),
        "format": "string",
    },
    "poetrymeter": {
        "description": "meter in which this verse is written",
        "format": "string",
    },
    "poetryverse": {
        "description": (
            "word is start of a verse of poetry, " "value is the number of the verse"
        ),
        "format": "number",
    },
    "fass": {
        "description": "number of the piece (bezel) that the word belongs to",
        "format": "number",
    },
    "lwcvl": {
        "description": "personal notes by Cornelis van Lit",
        "format": "string",
    },
    "quran": {
        "description": "word is part of a quran citation (sura:aya)",
        "format": "string",
    },
}

# DISTILL TABLE of CONTENTS

TOC_PAGES = (4, 5)

TOC_LINE_RE = re.compile(
    r"""
    ^
    ([٠-٩]+)
    ‐
    \s*
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

        curLine.append(f"{fields[-2]}{fields[-1]}")
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
    "extra": [
        "short",
        "haspunct",
        "punctafter",
        "punctbefore",
        "qunawims",
        "poetrymeter",
        "poetryverse",
        "fass",
        "lwcvl",
        "quran",
    ],
}


def convert(source, ocred, pages, versionTf):
    global pageNums
    global SRC_FILE
    global TYPE_MAP
    global HAS_TOC
    global TOC_SOURCE
    global OCRED
    global U
    global VERSION_TF
    global SEP
    global SKIPCOL
    global EXTRA

    U = UChar()

    pageNums = parseNums(pages)

    workInfo = WORKS[source]
    dest = getTfDest(source, versionTf)
    (SRC_FILE, OCRED) = getFile(source, ocred)
    HAS_TOC = workInfo.get("toc", False)
    TOC_SOURCE = workInfo.get("sourceToc", None)
    TYPE_MAP = TYPE_MAPS[OCRED]
    VERSION_TF = versionTf
    SEP = workInfo["sep"]
    SKIPCOL = workInfo.get("skipcol", None)
    EXTRA = workInfo.get("extra", False)

    cv = CV(Fabric(locations=dest))

    return cv.walk(
        director,
        slotType,
        otext=otext[None] | otext[OCRED],
        generic=generic(source),
        intFeatures=intFeatures[None] | intFeatures[OCRED],
        featureMeta=featureMeta[None]
        | featureMeta[OCRED]
        | (featureMeta["extra"] if EXTRA else {}),
        generateTf=True,
    )


# DIRECTOR


def director(cv):
    """Read tsv data fields.

    This is a function that does the work as indicated in the
    [walker converion engine of Text-Fabric](https://annotation.github.io/text-fabric/tf/convert/walker.html)
    See `fusus.convert` for a description of the fields in the TSV files.
    """

    stops = U.stops

    errors = collections.defaultdict(set)

    cur = [None, None, None, None]
    prev = [None, None, None, None]
    nSec = len(prev)

    def getData(dataFile, sep, extra):
        data = []

        with open(dataFile) as fh:
            next(fh)
            for line in fh:
                row = line.rstrip("\n").split(sep)
                if SKIPCOL is not None:
                    del row[SKIPCOL : SKIPCOL + 1]
                page = int(row[0])
                if pageNums is not None and page not in pageNums:
                    continue

                if OCRED:
                    row = (
                        page,
                        int(row[1]),
                        row[2],
                        int(row[3]),
                        *(None if c in {"", "?"} else int(c) for c in row[4:8]),
                        int(row[8]),
                        *row[9:11],
                    )
                else:
                    tail = (*row[10:13], row[9], *row[13:]) if extra else row[9:11]
                    row = (
                        page,
                        *(int(c) for c in row[1:4]),
                        row[4],
                        *(None if c in {"", "?"} else int(c) for c in row[5:9]),
                        *tail,
                    )

                data.append(row)
        return data

    data = getData(SRC_FILE, SEP, EXTRA)

    boxL = nSec if OCRED else nSec + 1

    if HAS_TOC:
        tocData = data
        if TOC_SOURCE:
            tocFile = f"{TOC_SOURCE['dir']}/{TOC_SOURCE['file']}"
            sep = TOC_SOURCE["sep"]
            tocData = getData(tocFile, sep, False)
        toc = getToc(tocData)
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

        lettersIndex = 9 if EXTRA else -2
        puncIndex = 10 if EXTRA else -1
        letters = fields[lettersIndex]
        punc = fields[puncIndex]

        puncBefore = None
        raw = None
        if EXTRA:
            puncBefore = fields[puncIndex + 1]
            raw = fields[puncIndex + 2]

        lettersp = Tr.asciiFromArabic(letters) if letters else ""
        lettersn = Tr.latinFromArabic(letters) if letters else ""
        letterst = Tr.standardFromArabic(letters) if letters else ""
        punca = Tr.asciiFromArabic(punc) if punc else ""

        s = cv.slot()
        cv.feature(
            s,
            boxl=fields[boxL],
            boxt=fields[boxL + 1],
            boxr=fields[boxL + 2],
            boxb=fields[boxL + 3],
            letters=letters,
            lettersp=lettersp,
            lettersn=lettersn,
            letterst=letterst,
        )
        cv.feature(s, punc=punc, punca=punca)
        if puncBefore is not None:
            puncba = Tr.asciiFromArabic(puncBefore) if puncBefore else ""
            cv.feature(s, puncb=puncBefore, puncba=puncba)
        if raw is not None:
            cv.feature(s, raw=raw)

        if EXTRA:
            extraData = {}
            if fields[13]:
                extraData["qunawims"] = fields[13]
            if fields[14]:
                extraData["poetrymeter"] = fields[14]
            if fields[15]:
                extraData["poetryverse"] = int(fields[15])
            if fields[16]:
                extraData["fass"] = int(fields[16])
            if fields[17]:
                extraData["lwcvl"] = fields[17]
            if fields[18]:
                extraData["quran"] = fields[18]
            cv.feature(s, **extraData)

        if any(c in stops for c in punc):
            cv.terminate(curSentence)
            curSentence = cv.node("sentence")
            nSentence += 1
            cv.feature(curSentence, n=nSentence)
        if OCRED:
            cv.feature(s, confidence=fields[-3])

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
        for (word, n) in api.F.letters.freqList()[0:20]:
            print(f"{n:>6} x {word}")
