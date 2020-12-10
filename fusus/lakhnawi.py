import collections
import re
from itertools import chain

from unicodedata import name as uname

from IPython.display import display, HTML, Image

import fitz

from tf.core.helpers import setFromSpec
from .parameters import SOURCE_DIR


NAME = "Lakhnawi"
SOURCE = f"{SOURCE_DIR}/{NAME}/{NAME.lower()}.pdf"
FONT = f"{SOURCE_DIR}/{NAME}/Font report {NAME}.pdf"
DEST = f"{SOURCE_DIR}/{NAME}/{NAME.lower()}.txt"

CSS = """
<style>
.r {
    font-family: normal, sans-serif;
    font-size: 24pt;
    direction: rtl;
}
p.r {
    text-align: right;
    direction: rtl;
}
.l {
    font-family: normal, sans-serif;
    font-size: 16pt;
    direction: ltr;
}
.c {
    font-family: monospace;
    font-size: 12pt;
    direction: ltr;
}
p.l {
    text-align: left;
    direction: ltr;
}
.p {
    font-family: monospace;
    font-size: 12pt;
    font-weight: bold;
    background-color: yellow;
    direction: ltr;
}
</style>
"""

PUA_RANGES = (("e000", "f8ff"),)

SEMITIC_RANGES = (
    ("0600", "06ff"),
    ("0750", "077f"),
    ("08a0", "08ff"),
    ("206c", "206d"),
    ("fb50", "fdfd"),
    ("fe70", "fefc"),
    ("0591", "05f4"),
    ("fb1d", "fb4f"),
)

NO_SPACING_RANGES = (("064b", "0652"),)

NEUTRAL_DIRECTION_RANGES = (
    ("0020", "002f"),
    ("003a", "0040"),
    ("005b", "0060"),
    ("007b", "00b1"),
    ("00b4", "00b8"),
    ("00ba", "00bf"),
    ("00f7", "00f7"),
    ("02d8", "02df"),
    ("02e5", "0362"),
    ("2000", "206f"),
)

REPLACE_DEF = """
0627+e815 => 0623+064e : ALIF-HAMZA + FATA
e80e+e807 => fefc      : LAM + ALEF LIGATURE
e821      =>           : TATWEEL (short)
e825      => 064e      : FATHA (high)
e826      => 064f      : DAMMA (high)
e828      => 0652      : SUKUN (high)
e830      => 064e+0651 : SHADDA+FATHA LIG => non-isolated, separate chars
e8e8      => 064e      : FATHA (mid)
e864      => 0650      : KASRA (low)
e8df      => 0650      : KASRA (low)
e8e9      => 064f      : DAMMA
fc60      => 064e+0651 : SHADDA+FATHA LIG => non-isolated, separate chars
"""


def getSetFromRanges(rngs):
    result = set()
    for (b, e) in rngs:
        for c in range(int(b, base=16), int(e, base=16) + 1):
            result.add(c)
    return result


REPLACE_RE = re.compile(r"""^([0-9a-z+]+)\s*=>\s*([0-9a-z+]*)\s*:\s*(.*)$""", re.I)


def getDictFromDef(defs):
    result = {}
    for line in defs.strip().split("\n"):
        match = REPLACE_RE.match(line)
        if not match:
            print(f"MALFORMED REPLACE DEF: {line}")
            continue
        (vals, repls, comment) = match.group(1, 2, 3)
        vals = vals.split("+")
        repls = [int(repl, base=16) for repl in repls.split("+")] if repls else []
        if len(vals) == 1:
            result[int(vals[0], base=16)] = repls
        elif len(vals) == 2:
            result.setdefault(int(vals[0], base=16), {})[int(vals[1], base=16)] = repls
        else:
            print(f"MORE THAN 2 SOURCE CHARS IN REPLACE DEF: {line}")
            continue
    return result


U_LINE_RE = re.compile(r"""^U\+([0-9a-f]{4})([0-9a-f ]*)$""", re.I)
HEX_RE = re.compile(r"""^[0-9a-f]{4}$""", re.I)


def showString(x):
    display(HTML(f"""<span class="r">{x}</span>"""))
    for c in x:
        display(
            HTML(
                f"""<p><span class="r">{c}</span>&nbsp;&nbsp;"""
                f"""<span class="c">{ord(c):>04x} {uname(c)}</span></p>"""
            )
        )


class Lakhnawi:
    def __init__(self):
        self.puas = getSetFromRanges(PUA_RANGES)
        self.semis = getSetFromRanges(SEMITIC_RANGES)
        self.neutrals = getSetFromRanges(NEUTRAL_DIRECTION_RANGES)
        self.nospacings = getSetFromRanges(NO_SPACING_RANGES)
        self.replace = getDictFromDef(REPLACE_DEF)
        self.rls = self.puas | self.semis
        self.getCharInfo()
        self.doc = fitz.open(SOURCE)
        self.text = {}

    def setStyle(self):
        display(HTML(CSS))

    def getCharInfo(self):
        self.doubles = {}
        self.privates = set()
        doubles = self.doubles
        privates = self.privates
        puas = self.puas

        doc = fitz.open(FONT)

        for page in doc:
            textPage = page.getTextPage()
            data = textPage.extractText()

            for (ln, line) in enumerate(data.split("\n")):
                if line.startswith("U+"):
                    match = U_LINE_RE.match(line)
                    if not match:
                        continue
                    (main, rest) = match.group(1, 2)
                    main = main.lower()
                    nMain = int(main, base=16)
                    if nMain in puas:
                        privates.add(nMain)
                        continue
                    if nMain == 0:
                        continue
                    second = None
                    rest = rest.replace(" ", "")
                    if rest:
                        if HEX_RE.match(rest):
                            second = rest.lower()
                    if second:
                        nSecond = int(second, base=16)
                        if nSecond > nMain:
                            doubles[nMain] = nSecond
                        else:
                            doubles[nSecond] = nMain

    def parsePageNums(self, pageNumSpec):
        doc = self.doc
        pageNums = (
            list(range(1, len(doc) + 1))
            if not pageNumSpec
            else [pageNumSpec]
            if type(pageNumSpec) is int
            else setFromSpec(pageNumSpec)
            if type(pageNumSpec) is str
            else list(pageNumSpec)
        )
        return [i for i in sorted(pageNums) if 0 < i <= len(doc)]

    def drawPages(self, pageNumSpec):
        doc = self.doc

        for pageNum in self.parsePageNums(pageNumSpec):
            page = doc[pageNum - 1]

            pix = page.getPixmap(matrix=fitz.Matrix(4, 4), alpha=False)
            display(Image(data=pix.getPNGData(), format="png"))

    def getPages(self, pageNumSpec):
        for pageNum in self.parsePageNums(pageNumSpec):
            self.pageNum = pageNum
            doc = self.doc
            page = doc[pageNum - 1]

            textPage = page.getTextPage()
            data = textPage.extractRAWDICT()
            self.collectPage(data)

    def plainPages(self, pageNumSpec):
        for pageNum in self.parsePageNums(pageNumSpec):
            lines = self.text.get(pageNum, [])

            for (i, line) in enumerate(lines):
                print(self.plainLine(line))

    def htmlPages(self, pageNumSpec):
        for pageNum in self.parsePageNums(pageNumSpec):
            lines = self.text.get(pageNum, [])

            html = []

            for (i, line) in enumerate(lines):
                html.append(f"""<p class="r">{self.htmlLine(line)}</p>\n""")
            display(HTML("".join(html)))

    def showInfo(self, pageNumSpec):
        pageNums = self.parsePageNums(pageNumSpec)
        text = self.text
        puas = self.puas

        puasOut = collections.defaultdict(collections.Counter)

        texts = {pageNum: text[pageNum] for pageNum in pageNums if pageNum in text}

        for (pageNum, pageText) in texts.items():
            for line in pageText:
                for char in line:
                    c = char[-1]
                    for d in c:
                        ud = ord(d)
                        if ud in puas:
                            puasOut[f"{ud:>04x}"][pageNum] += 1

        totalChars = len(puasOut)
        totalPages = len(set(chain.from_iterable(puasOut.values())))
        totalOccs = sum(sum(pns.values()) for pns in puasOut.values())

        charRep = "character" + ("" if totalChars == 1 else "s")
        occRep = "occurence" + ("" if totalOccs == 1 else "s")
        pageRep = "page" + ("" if totalPages == 1 else "s")

        print(
            f"{totalChars} private use {charRep} in text"
            f" in {totalOccs} {occRep} on {totalPages} {pageRep}"
        )
        for xc in sorted(puasOut):
            pageNums = puasOut[xc]
            nPageNums = len(pageNums)
            pageRep = "page" + ("" if nPageNums == 1 else "s")
            thistotal = sum(pageNums.values())
            print(f"{xc}: {thistotal} x on {nPageNums} {pageRep}")
            for pn in sorted(pageNums):
                occs = pageNums[pn]
                print(f"\t\t\tpage {pn:>3}: {occs:>3} x")

    def collectPage(self, data):
        doubles = self.doubles
        puas = self.puas
        pageNum = self.pageNum

        chars = []
        prevChar = None
        prevFont = None
        prevSize = None

        def addChar():
            box = tuple(int(round(x * 10)) for x in prevChar["bbox"])
            c = prevChar["c"]
            uc = ord(c)
            try:
                un = uname(c)
            except Exception:
                un = "NO NAME"
            chars.append(
                (
                    *box,
                    prevFont,
                    prevSize,
                    f"{uc:>04x}",
                    "PRIVATE" if uc in puas else un,
                    c,
                )
            )

        def collectChars(data, font, size):
            nonlocal prevChar
            nonlocal prevFont
            nonlocal prevSize

            if type(data) is list:
                for elem in data:
                    collectChars(elem, font, size)

            elif type(data) is dict:
                if "font" in data:
                    font = data["font"]
                if "size" in data:
                    size = data["size"]
                if "c" in data:
                    c = data["c"]
                    uc = ord(c)
                    skip = False

                    if prevChar is not None:
                        pc = prevChar["c"]
                        puc = ord(pc)
                        if puc in doubles and doubles[puc] == uc:
                            skip = True
                        if uc in doubles and doubles[uc] == puc:
                            prevChar = data
                            skip = True

                    if not skip:
                        if prevChar is not None:
                            addChar()
                        prevChar = data
                        prevFont = font
                        prevSize = size

                for (k, v) in data.items():
                    if type(v) in {list, dict}:
                        collectChars(v, font, size)

        collectChars(data, None, None)
        if prevChar is not None:
            addChar()

        clusterKeyCharV = clusterVert(chars)
        lines = {}
        for char in sorted(chars, key=lambda c: (clusterKeyCharV(c), -keyCharH(c))):
            k = clusterKeyCharV(char)
            lines.setdefault(k, []).append(char)
        self.text[pageNum] = tuple(self.trimLine(line) for line in lines.values())

    def trimLine(self, chars):
        replace = self.replace

        result = []

        for char in chars:
            char = list(char)
            c = char[-1]
            uc = ord(c)

            if result:
                prevChar = result[-1]
                pc = prevChar[-1]
                if len(pc) == 1:
                    puc = ord(prevChar[-1])
                    if puc in replace:
                        repls = replace[puc]
                        if type(repls) is dict and uc in repls:
                            ucs = repls[uc]
                            if len(ucs) == 0:
                                result.pop()
                                continue

                            (puc, *ucs) = ucs
                            result[-1][-1] = chr(puc)
                            char[-1] = "".join(chr(u) for u in ucs)
                            result.append(char)
                            continue

            if uc in replace:
                repls = replace[uc]
                if type(repls) is list:
                    if len(repls) == 0:
                        continue

                    char[-1] = "".join(chr(u) for u in repls)
                    result.append(char)
                    continue

            result.append(char)

        return result

    def plainLine(self, chars):
        return "".join(c[-1] for c in chars)

    def htmlLine(self, chars):
        puas = self.puas
        nospacings = self.nospacings
        neutrals = self.neutrals
        rls = self.rls

        result = []
        text = []
        prevLeft = None
        prevDir = "r"

        for char in chars:
            left = int(round(char[0]))
            right = int(round(char[2]))

            if prevLeft is not None:
                if prevLeft - right >= 25:
                    text.append(" ")

            c = char[-1]
            if c == "":
                prevLeft = left
                continue

            uc = ord(c[-1])

            if uc not in nospacings:
                prevLeft = left

            thisDir = prevDir if uc in neutrals else "r" if uc in rls else "l"

            if prevDir != thisDir:
                if text:
                    result.append(f"""<span class="{prevDir}">{"".join(text)}</span>""")
                text = []
                prevDir = thisDir

            rep = c
            for d in c:
                ud = ord(d)
                if ud in puas:
                    rep = f"""<span class="p">[{ud:>04x}]</span>"""
            text.append(rep)

        if text:
            result.append(f"""<span class="{prevDir}">{"".join(text)}</span>""")

        return "".join(result)


def keyCharV(char):
    return int(round((char[3] + char[1]) / 2))


def keyCharH(char):
    return char[2]


def clusterVert(data):
    keys = collections.Counter()
    for char in data:
        k = keyCharV(char)
        keys[k] += 1

    peaks = sorted(keys)
    if len(peaks) > 1:
        nDistances = len(peaks) - 1
        avPeakDist = int(
            round(sum(peaks[i + 1] - peaks[i] for i in range(nDistances)) / nDistances)
        )

        peakThreshold = int(round(avPeakDist / 3))
        clusteredPeaks = {}
        for (k, n) in sorted(keys.items(), key=lambda x: (-x[1], x[0])):
            added = False
            for kc in clusteredPeaks:
                if abs(k - kc) <= peakThreshold:
                    clusteredPeaks[kc].add(k)
                    added = True
                    break
            if not added:
                clusteredPeaks[k] = {k}
    toCluster = {}
    for (kc, ks) in clusteredPeaks.items():
        for k in ks:
            toCluster[k] = kc

    def clusterKeyCharV(char):
        k = keyCharV(char)
        return toCluster[k]

    if False:
        print("PEAKS")
        for k in peaks:
            print(f"{k:>4} : {keys[k]:>4}")
        print("CLUSTERED_PEAKS")
        for kc in sorted(clusteredPeaks):
            peak = ", ".join(f"{k:>4}" for k in sorted(clusteredPeaks[kc]))
            print(f"{peak} : {sum(keys[k] for k in clusteredPeaks[kc]):>4}")

    return clusterKeyCharV
