import collections
import re
import pprint as pp

from itertools import chain
from unicodedata import name as uname

from IPython.display import display, HTML, Image

import fitz

from tf.core.helpers import setFromSpec
from .parameters import SOURCE_DIR

PP = pp.PrettyPrinter(indent=2)


def pprint(x):
    PP.pprint(x)


NAME = "Lakhnawi"
SOURCE = f"{SOURCE_DIR}/{NAME}/{NAME.lower()}.pdf"
FONT = f"{SOURCE_DIR}/{NAME}/Font report {NAME}.pdf"
DEST = f"{SOURCE_DIR}/{NAME}/{NAME.lower()}.txt"

CSS = """
<style>
.r {
    font-family: normal, sans-serif;
    font-size: xx-large;
    direction: rtl;
}
.rc, .lc {
    font-family: normal, sans-serif;
    font-size: xx-large;
    background-color: white;
    border: 2pt solid #ffcccc;
}
.rc {
    direction: rtl;
}
.lc {
    direction: ltr;
    unicode-bidi: isolate-override;
}
p {
    text-align: left;
    direction: ltr;
}
p.r {
    text-align: right;
    direction: rtl;
}
.l {
    font-family: normal, sans-serif;
    font-size: medium;
    direction: ltr;
    unicode-bidi: isolate-override;
}
.c {
    font-family: monospace;
    font-size: x-small;
    direction: ltr;
}
.p {
    font-family: monospace;
    font-size: medium;
    font-weight: bold;
    background-color: yellow;
    direction: ltr;
}
.lrg {
    font-size: xx-large;
    font-weight: bold;
}
td {
    text-align: left ! important;
}
div.cn {
    text-align: center
}
span.cni {
    background-color: #eeeeee;
    padding-top: 4pt;
    padding-bottom: 4pt;
    padding-left: 8pt;
    padding-right: 8pt;
    border: 2pt solid #66aaaa;
    display: inline-block;
}
div.ch {
    border: 2pt solid #cccccc;
    background-color: #ddffff;
    display: inline-flex;
    flex-flow: column nowrap;
    max-width: 10em;
}
div.sr {
    display: flex;
    flex-flow: row wrap;
    direction: rtl;
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
    ("206a", "206f"),
    ("fb1d", "fb4f"),
)

NO_SPACING_RANGES = (("064b", "0652"),)

BRACKET_RANGES = (
    ("0028", "0029"),  # parentheses
    ("003c", "003c"),  # less than
    ("003e", "003e"),  # greater than
    ("005b", "005b"),  # left  sq bracket
    ("005d", "005d"),  # right sq bracket
    ("007b", "007b"),  # left  brace
    ("007d", "007d"),  # right brace
    ("00ab", "00ab"),  # left  guillemet double
    ("00bb", "00bb"),  # right guillemet double
    ("2018", "201d"),  # qutation marks directed
    ("2039", "203a"),  # guillemets single
    ("2045", "2046"),  # sqare brackets with quill
    ("204c", "204d"),  # bullets directed
)

DIRECTION_RANGES = (
    ("202a", "202e"),  # control writing direction
    ("2066", "2069"),  # control writing direction
)

NEUTRAL_DIRECTION_RANGES = (
    ("0020", "0020"),
    ("2000", "2017"),
    ("201e", "2029"),
    ("202f", "2038"),
    ("203b", "2044"),
    ("204a", "2044"),
    ("2056", "2064"),
    ("201e", "206f"),
)

REPLACE_DEF = """
0627+0648+e815 => 0623+064e+0648 : ALIF+x+HAMZA|FATA => ALIF|HAMZA+FATA+x
0627+e80a+e815 => 0623+064e+e80a : ALIF+x+HAMZA|FATA => ALIF|HAMZA+FATA+x
0627+fe97+e816 => 0623+064f+fe97 : ALIF+x+HAMZA|DAMMA => ALIF|HAMZA+DAMMA+x
0627+e815      => 0623+064e      : ALIF+HAMZA|FATA => ALIF|HAMZA+FATA
0627+e816      => 0623+064f      : ALIF+HAMZA|DAMMA => ALIF|HAMZA+DAMMA
e80a+e806      => fefb           : LAM/ALEF LIGATURE (isolated)
e80e+e807      => fefc           : LAM/ALEF LIGATURE (final)
e821+e82b      => 0670+0640      : TATWEEL+SUPERSCRIPT ALEF
e821           => 0640           : TATWEEL (short)
e823           => 064b           : FATHATAN (high)
e825           => 064e           : FATHA (high)
e826           => 064f           : DAMMA (high)
e827           => 0651           : SHADDA (high)
e828           => 0652           : SUKUN (high)
e82b           => 0670           : SUPERSCRIPT ALEF
e830           => fcf2           : FATHA|SHADDA medial
e831           => fcf3           : DAMMA|SHADDA medial
e832           => fcf4           : SHADDA|KASRA medial
e833           => 0651+0670      : SHADDA+SUPERSCRIPT ALEF
e845           => 0655+0650      : HAMZA+KASRA (low)
e864           => 0650           : KASRA (low)
e887           => 064d           : KASRATAN (low)
e888           => 0650           : KASRA (low)
e8d4           => fee0           : LAM (medial)
e8df           => 0650           : KASRA (low)
e8e8           => 064e           : FATHA (mid)
e8e9           => 064f           : DAMMA
e8ea           => 0651           : SHADDA (mid)
e8eb           => 0652           : SUKUN
fc60           => 064e+0651      : SHADDA|FATHA LIG => SHADDA+FATHA
"""


def uName(c):
    try:
        un = uname(c)
    except Exception:
        un = "NO NAME"
    return un


def getSetFromRanges(rngs):
    result = set()
    for (b, e) in rngs:
        for c in range(int(b, base=16), int(e, base=16) + 1):
            result.add(c)
    return result


def numericString(s):
    return "".join(f"⌊{ord(c):>04x}⌋" for c in s)


REPLACE_RE = re.compile(r"""^([0-9a-z+]+)\s*=>\s*([0-9a-z+]*)\s*:\s*(.*)$""", re.I)


def getDictFromDef(defs):
    rules = []
    for line in defs.strip().split("\n"):
        parts = line.split("#", maxsplit=1)
        if len(parts) > 1:
            line = parts[0]
        line = line.strip()
        if not line:
            continue
        match = REPLACE_RE.match(line)
        if not match:
            print(f"MALFORMED REPLACE DEF: {line}")
            continue
        (vals, repls, comment) = match.group(1, 2, 3)
        vals = tuple(chr(int(val, base=16)) for val in vals.split("+"))
        repls = (
            tuple(chr(int(repl, base=16)) for repl in repls.split("+")) if repls else ()
        )
        rules.append((vals, repls))

    result = {}

    for (vals, repls) in sorted(rules, key=lambda x: (-len(x[0]), x[0])):
        result.setdefault(vals[0], []).append((vals[1:], repls))

    return result


def parseNums(numSpec):
    return (
        None
        if not numSpec
        else [numSpec]
        if type(numSpec) is int
        else setFromSpec(numSpec)
        if type(numSpec) is str
        else list(numSpec)
    )


U_LINE_RE = re.compile(r"""^U\+([0-9a-f]{4})([0-9a-f ]*)$""", re.I)
HEX_RE = re.compile(r"""^[0-9a-f]{4}$""", re.I)
PUA_RE = re.compile(r"""⌊([^⌋]*)⌋""")


class Lakhnawi:
    def __init__(self):
        self.getCharConfig()
        self.doc = fitz.open(SOURCE)
        self.text = {}
        self.lines = {}

    def setStyle(self):
        display(HTML(CSS))

    def getCharConfig(self):
        self.puas = getSetFromRanges(PUA_RANGES)
        self.semis = getSetFromRanges(SEMITIC_RANGES)
        self.neutrals = getSetFromRanges(NEUTRAL_DIRECTION_RANGES)
        self.nospacings = getSetFromRanges(NO_SPACING_RANGES)
        self.replace = getDictFromDef(REPLACE_DEF)
        self.rls = self.puas | self.semis
        self.getCharInfo()

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

    def showChar(self, c):
        puas = self.puas
        rls = self.rls

        xc = ord(c)
        ccode = f"""<span class="{"p" if xc in puas else "c"}">{xc:>04x}</span>"""
        crep = (
            "??"
            if xc in puas
            else f"""<span class="{"rc" if xc in rls else "lc"}">{c}"""
        )
        cname = "" if xc in puas else f"""<span class="c">{uName(c)}</span>"""

        return f"""
<div class="ch">
    <div class="cn">{ccode}</div>
    <div class="cn"><span class="cni">{crep}</span></div>
    <div class="cn">{cname}</div>
</div>
"""

    def showString(self, s):
        display(HTML(f"""<p><span class="r">{s}</span></p>"""))
        display(
            HTML(
                """<div class="sr">"""
                + ("".join(self.showChar(c) for c in s) + "</div>")
            )
        )

    def showReplacements(self):
        replace = self.replace

        html = []
        html.append("<table>")

        for val in sorted(replace):
            rules = replace[val]
            for (vals, repls) in rules:
                valRep = "".join(self.showChar(c) for c in (val,) + vals)
                replRep = "".join(self.showChar(c) for c in repls)
                html.append(
                    f"""
<tr>
    <td>{valRep}</td>
    <td><span class="lrg">⇒</span></td>
    <td>{replRep}</td>
</tr>
"""
                )

        html.append("<table>")
        display(HTML("".join(html)))

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

    def getPages(self, pageNumSpec, refreshConfig=False, debug=False):
        if refreshConfig:
            self.getCharConfig()

        for pageNum in self.parsePageNums(pageNumSpec):
            self.pageNum = pageNum
            doc = self.doc
            page = doc[pageNum - 1]

            textPage = page.getTextPage()
            data = textPage.extractRAWDICT()
            self.collectPage(data, debug=debug)

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

    def showLines(self, pageNumSpec, lineSpec, charSpec):
        lines = self.lines
        pageNums = self.parsePageNums(pageNumSpec)
        lineNums = parseNums(lineSpec)
        charNums = parseNums(charSpec)
        if charNums is not None:
            charNums = set(charNums)

        myLines = {pageNum: lines[pageNum] for pageNum in pageNums if pageNum in lines}

        html = []
        html.append("<table>")
        html.append(
            """
<tr>
    <th>seq</th>
    <th>bottom</th>
    <th>height</th>
    <th>width</th>
    <th>shift</th>
    <th>after</th>
    <th>font</th>
    <th>size</th>
    <th>char</th>
</tr>
"""
        )

        for (pageNum, pageLines) in myLines.items():
            myLineNums = (
                range(1, len(pageLines) + 1)
                if lineNums is None
                else [ln for ln in lineNums if 0 < ln <= len(pageLines)]
            )
            for ln in myLineNums:
                chars = pageLines[ln - 1]
                nChars = len(chars)
                html.append(
                    f"""
<tr>
    <th colspan=3>page {pageNum}</th>
    <th colspan=2>line {ln}</th>
    <th colspan=3>{nChars} characters</th>
</tr>
"""
                )
                for (i, char) in enumerate(chars):
                    (le, to, ri, bo, font, size, c) = char
                    if charNums is not None and i + 1 not in charNums:
                        continue
                    after = "x" if i == nChars - 1 else le - chars[i + 1][2]
                    shift = (
                        "x"
                        if i == nChars - 1
                        else keyCharH(char) - keyCharH(chars[i + 1])
                    )
                    html.append(
                        f"""
<tr>
    <td><b>{i + 1}</b></td>
    <td>{bo}</td>
    <td>{bo - to}</td>
    <td>{ri - le}</td>
    <td>{shift}</td>
    <td>{after}</td>
    <td>{font}</td>
    <td>{size}pt</td>
    <td>{"".join(self.showChar(x) for x in c)}</td>
</tr>
"""
                    )

        html.append("</table>")
        display(HTML("".join(html)))

    def showUsedChars(self, pageNumSpec, onlyPuas=False, long=False):
        pageNums = self.parsePageNums(pageNumSpec)
        text = self.text

        charsOut = collections.defaultdict(collections.Counter)

        texts = {pageNum: text[pageNum] for pageNum in pageNums if pageNum in text}

        for (pageNum, pageText) in texts.items():
            for line in pageText:
                for span in line:
                    thesePuas = PUA_RE.findall(span[1])
                    for pua in thesePuas:
                        charsOut[chr(int(pua, base=16))][pageNum] += 1
                    if not onlyPuas:
                        rest = PUA_RE.sub("", span[1])
                        for c in rest:
                            charsOut[c][pageNum] += 1

        totalChars = len(charsOut)
        totalPages = len(set(chain.from_iterable(charsOut.values())))
        totalOccs = sum(sum(pns.values()) for pns in charsOut.values())

        charRep = "character" + ("" if totalChars == 1 else "s")
        occRep = "occurence" + ("" if totalOccs == 1 else "s")
        pageRep = "page" + ("" if totalPages == 1 else "s")

        label = "private use " if onlyPuas else ""

        html = []
        html.append(
            f"""
<p><b>{totalChars} {label}{charRep} in {totalOccs} {occRep}
on {totalPages} {pageRep}</b></p>
<table>
"""
        )
        for c in sorted(charsOut):
            pageNums = charsOut[c]
            nPageNums = len(pageNums)
            pageRep = "page" + ("" if nPageNums == 1 else "s")
            thistotal = sum(pageNums.values())
            html.append(
                f"""
<tr>
    <td>{self.showChar(c)}</td>
    <td><b>{thistotal}</b> on <i>{nPageNums}</i> {pageRep}</td>
</tr>
"""
            )
            if long:
                for pn in sorted(pageNums):
                    occs = pageNums[pn]
                    html.append(
                        f"""
<tr>
    <td></td>
    <td><i>page {pn:>3}</i>: <b>{occs:>3}</b></td>
</tr>
"""
                    )
        html.append("</table>")
        display(HTML("".join(html)))

    def collectPage(self, data, debug=False):
        doubles = self.doubles
        pageNum = self.pageNum

        chars = []
        prevChar = None
        prevFont = None
        prevSize = None

        def addChar():
            box = tuple(int(round(x * 10)) for x in prevChar["bbox"])
            c = prevChar["c"]
            chars.append(
                (
                    *box,
                    prevFont,
                    prevSize,
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
                    if c == " ":
                        skip = True

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
            lines.setdefault(k, []).append(list(char))

        self.lines[pageNum] = tuple(lines.values())
        self.text[pageNum] = tuple(
            self.trimLine(line, debug=debug) for line in lines.values()
        )

    def trimLine(self, chars, debug=False):
        replace = self.replace
        puas = self.puas
        nospacings = self.nospacings
        neutrals = self.neutrals
        rls = self.rls

        nChars = len(chars)

        for (i, char) in enumerate(chars):
            c = char[-1]
            if c in replace:
                rules = replace[c]
                for (vals, repls) in rules:
                    if debug:
                        ruleRep = (
                            f"""{numericString(c)}{numericString("".join(vals)):<20}"""
                            """ ⇒ """
                            f"""{numericString("".join(repls)):<20}"""
                        )

                    nVals = len(vals)
                    if i + nVals >= nChars:
                        if debug:
                            print(f"{i:>4} * {ruleRep}")
                        continue
                    if not all(vals[j] == chars[i + j + 1][-1] for j in range(nVals)):
                        if debug:
                            print(f"{i:>4} x {ruleRep}")
                        continue

                    if len(repls) == 0:
                        chars[i][-1] = ""
                    else:
                        chars[i][-1] = repls[0]
                        repls = repls[1:]
                        nRepls = len(repls)

                        for (j, val) in enumerate(vals):
                            chars[i + j + 1][-1] = repls[j] if j < nRepls else ""

                    if nRepls > nVals:
                        chars[i + nVals][-1] += "".join(repls[nVals:])
                    if debug:
                        resRep = "".join(
                            f"{numericString(c[-1])}" for c in chars[i : i + nVals + 1]
                        )
                        print(f"{i:>4} V {ruleRep}: {resRep}")
                    break

        result = []
        prevLeft = None
        prevDir = "r"
        outChars = []

        def addChars():
            if outChars:
                charsRep = "".join(outChars if prevDir == "r" else reversed(outChars))
                result.append((prevDir, charsRep))

        for char in chars:
            left = int(round(char[0]))
            right = int(round(char[2]))

            if prevLeft is not None:
                if prevLeft - right >= 25:
                    outChars.append(" ")

            c = char[-1]
            if c == "":
                prevLeft = left
                continue

            uc = ord(c[-1])

            if uc not in nospacings:
                prevLeft = left

            thisDir = prevDir if uc in neutrals else "r" if uc in rls else "l"

            if prevDir != thisDir:
                addChars()
                outChars = []
                prevDir = thisDir

            rep = c
            for d in c:
                ud = ord(d)
                if ud in puas:
                    rep = f"""⌊{ud:>04x}⌋"""
            outChars.append(rep)

        addChars()

        return result

    def plainLine(self, spans):
        return "".join("".join(span[1]) for span in spans)

    def htmlLine(self, spans):
        result = []

        for (textDir, string) in spans:
            rep = string.replace("⌊", """<span class="p">""").replace("⌋", "</span>")
            result.append(f"""<span class="{textDir}">{rep}</span>""")

        return "".join(result)


def keyCharV(char):
    return int(round((char[3] + char[1]) / 2))


def keyCharH(char):
    return char[2]
    # return char[0] + (char[2] - char[0]) / 2
    # return char[0]


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
