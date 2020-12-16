import sys
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
    font-size: xx-large;
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
div.ch.p {
    background-color: #ffeedd;
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

ARABIC_RANGES = (
    ("0600", "06ff"),
    ("0750", "077f"),
    ("08a0", "08ff"),
    ("206a", "206f"),
    ("fb50", "fdc7"),
    ("fdf0", "fdfd"),
    ("fe70", "fefc"),
)

SYRIAC_RANGES = (
    ("0700", "074f"),
    ("2670", "2671"),
)

HEBREW_RANGES = (
    ("0590", "05ff"),
    ("0fb1d", "fb4f"),
)

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

NO_SPACING_RANGES = (
    ("060c", "060c"),
    ("064b", "065f"),
    ("fc5e", "fc63"),
    ("fcf2", "fcf4"),
    ("fe77", "fe77"),
    ("fe79", "fe79"),
    ("fe7b", "fe7b"),
    ("fe7d", "fe7d"),
    ("fe7f", "fe7f"),
)

DIACRITIC_RANGES = (
    ("064b", "065f"),
    ("064b", "065f"),
    ("fc5e", "fc63"),
    ("fcf2", "fcf4"),
    ("fe77", "fe77"),
    ("fe79", "fe79"),
    ("fe7b", "fe7b"),
    ("fe7d", "fe7d"),
    ("fe7f", "fe7f"),
)

PRIVATE_SPACE = "\uea75"

PRIVATE_LETTERS_DEF = """
e800
e806
e807
e808
e809
e80a
e80e
e898
e8d4
e8e9
e915
e917
ea79
"""

PRIVATE_DIAS_DEF = """
e812
e814
e815
e816
e817
e818
e81d
e821
e823
e824
e825
e826
e827
e828
e829
e82b
e82e
e82f
e830
e831
e832
e833
e834
e835
e837
e838
e839
e83a
e83f
e840
e845
e846
e849
e84d
e85b
e85c
e863
e864
e86d
e87f
e880
e887
e888
e8de
e8df
e8e6
e8e7
e8e8
e8e9
e8ea
e8eb
e8ee
e8f4
e8f5
e8f6
e8f8
e8fb
e8fe
"""


REPLACE_DEF = """
# 0627+0646+e815 => 0623+064e+0646 : ALIF+x+HAMZA/FATA => ALIF/HAMZA+FATA+x
# 0627+0648+e815 => 0623+064e+0648 : ALIF+x+HAMZA/FATA => ALIF/HAMZA+FATA+x
# 0627+e80a+e815 => 0623+064e+e80a : ALIF+x+HAMZA/FATA => ALIF/HAMZA+FATA+x
# 0627+fe97+e816 => 0623+064f+fe97 : ALIF+x+HAMZA/DAMMA => ALIF/HAMZA+DAMMA+x
# e821+064e      => 064e+0640      : TATWEEL+FATHA => FATHA+TATWEEL
# e821+e825      => 064e+0640      : TATWEEL+FATHA => FATHA+TATWEEL
# e821+064f      => 0650+064f      : TATWEEL+DAMMA => DAMMA+TATWEEL
# e821+e8e9      => 0650+064f      : TATWEEL+DAMMA => DAMMA+TATWEEL
# e821+0650      => 0650+0640      : TATWEEL+KASRA => KASRA+TATWEEL
# e821+e864      => 0650+0640      : TATWEEL+KASRA => KASRA+TATWEEL
# e821+0652      => 0652+0640      : TATWEEL+SUKUN => SUKUN+TATWEEL
# e821+e828      => 0652+0640      : TATWEEL+SUKUN => SUKUN+TATWEEL
# e821+fc60      => 064e+0651      : TATWEEL+SHADDA/FATHA => SHADDA+FATHA
# e821           => 0640           : TATWEEL (short)
# fefb+062f+e85b => fef7+064e+062f : LAM/ALEF+x+HAMZA/FATHA => LAM/ALEF/HAMZA+FATHA+x

0627+e815        => 0623+064e      : ALIF+HAMZA/FATA => ALIF/HAMZA+FATA
0627+c+e815      => 0623+064e+c    : ALIF+letter+HAMZA/FATA => ALIF/HAMZA+FATA+letter
0627+e816        => 0623+064f      : ALIF+HAMZA/DAMMA => ALIF/HAMZA+DAMMA
0627+e846        => 0625+064d      : ALIF+HAMZAlow/KASHRATAN => ALIF/HAMZA+KASHRATAN
e80a+e806        => fefb           : LAM/ALEF(isol)
e80a+d+e806      => fefb+d         : LAM/ALEF(isol) with diacritic
e80a+d+e806+e85b => fef7+d         : LAM/ALEF/HAMZA(isol) with diacritic
e80a+e808        => 0644+0671      : LAM+ALEF(wasla) [1]
e80e+e807        => fefc           : LAM/ALEF(final)
e80e+d+e807      => fefc+d         : LAM/ALEF(final) with diacritic
e80e+e821+d+e807 => fefc+d         : LAM/ALEF(final) with tatweel,diacritic
e821             =>                : (ignore short tatweel)
e823             => 064b           : FATHATAN
e824             => 064c           : DAMMATAN
e825             => 064e           : FATHA
e826             => 064f           : DAMMA
e827             => 0651           : SHADDA
e828             => 0652           : SUKUN
e82b             => 0670           : ALEF(super)
e830             => fcf2           : FATHA/SHADDA(medial)
e831             => fcf3           : DAMMA/SHADDA(medial)
e832             => fcf4           : SHADDA/KASRA(medial)
e833             => 0651+0670      : SHADDA+ALEF(super)
e845             => 0655+0650      : HAMZAlow+KASRA
fefb+e85b        => fef7+064e      : LAM/ALEF/HAMZA(isol)+FATHA
e863             => 064d           : KASRATAN
e864             => 0650           : KASRA
e887             => 064d           : KASRATAN
e888             => 0650           : KASRA
e8d4             => fee0           : LAM(medial)
e8df             => 0650           : KASRA
e8e8             => 064e           : FATHA
e8e9             => 064f           : DAMMA
e8ea             => 0651           : SHADDA
e8eb             => 0652           : SUKUN
e8f4             => 064e+0651      : SHADDA/FATHA => SHADDA+FATHA
fc60             => 064e+0651      : SHADDA/FATHA => SHADDA+FATHA

# [1] it should be a LAM/ALEF ligature with wasla, but there is no such unicode char
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
        for uc in range(int(b, base=16), int(e, base=16) + 1):
            result.add(chr(uc))
    return result


def ptRep(p):
    return int(round(p * 10))


REPLACE_RE = re.compile(r"""^([0-9a-z+]+)\s*=>\s*([0-9a-z+]*)\s*:\s*(.*)$""", re.I)


def getSetFromDef(defs):
    return {chr(int(item, base=16)) for item in defs.strip().split("\n")}


LETTER_CODE_DEF = dict(
    c=(2, "letter"),
    d=(1, "diacritic"),
)


LETTER_CODE = {cd: info[0] for (cd, info) in LETTER_CODE_DEF.items()}
CODE_LETTER = {info[0]: cd for (cd, info) in LETTER_CODE_DEF.items()}
LETTER_KIND = {info[0]: info[1] for info in LETTER_CODE_DEF.values()}


def getDictFromDef(defs):
    rules = []
    rn = 0
    good = True

    for (i, line) in enumerate(defs.strip().split("\n")):
        parts = line.split("#", maxsplit=1)
        if len(parts) > 1:
            line = parts[0]
        line = line.strip()
        if not line:
            continue
        match = REPLACE_RE.match(line)
        if not match:
            print(f"MALFORMED REPLACE DEF @{i}: {line}")
            good = False
            continue

        rn += 1
        (valStr, replStr, comment) = match.group(1, 2, 3)

        vals = []
        d = None
        for (i, val) in enumerate(valStr.split("+")):
            if val in {"c", "d"}:
                if d is not None:
                    print(f"MULTIPLE d in RULE @{i}: rule {rn}: {line}")
                    good = False
                d = i
                vals.append(LETTER_CODE[val])
            else:
                vals.append(chr(int(val, base=16)))

        repls = []
        e = None
        if replStr:
            for (i, repl) in enumerate(replStr.split("+")):
                if repl in {"c", "d"}:
                    if e is not None:
                        print(f"MULTIPLE d in RULE @{i}: rule {rn}: {line}")
                        good = False
                    e = i
                    repls.append(LETTER_CODE[repl])
                else:
                    repls.append(chr(int(repl, base=16)))

        if d is None and e is not None:
            print(f"d in REPLACEMENT but not in MATCH @[i]: rule {rn}: {line}")
            good = False

        rules.append((rn, tuple(vals), d, tuple(repls), e))

    if not good:
        return None

    result = {}
    ruleIndex = {}

    for (rn, vals, d, repls, e) in sorted(rules, key=lambda x: (-len(x[1]), x[1])):
        result.setdefault(vals[0], []).append((rn, vals, d, repls, e))
        ruleIndex[rn] = (vals, d, repls, e)

    return (result, ruleIndex)


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
        self.good = True
        self.rulesApplied = collections.defaultdict(collections.Counter)

    def setStyle(self):
        display(HTML(CSS))

    def getCharConfig(self):
        self.puas = getSetFromRanges(PUA_RANGES)
        self.arabic = getSetFromRanges(ARABIC_RANGES)
        self.hebrew = getSetFromRanges(HEBREW_RANGES)
        self.syriac = getSetFromRanges(SYRIAC_RANGES)
        self.semis = self.arabic | self.hebrew | self.syriac
        self.neutrals = getSetFromRanges(NEUTRAL_DIRECTION_RANGES)
        self.privateLetters = getSetFromDef(PRIVATE_LETTERS_DEF)
        self.privateDias = getSetFromDef(PRIVATE_DIAS_DEF)
        self.privateSpace = PRIVATE_SPACE
        self.nospacings = getSetFromRanges(NO_SPACING_RANGES) | self.privateDias
        self.diacritics = getSetFromRanges(DIACRITIC_RANGES) | self.privateDias
        self.arabicLetters = self.arabic - self.diacritics
        (self.replace, self.ruleIndex) = getDictFromDef(REPLACE_DEF)
        if self.replace is None:
            self.replace = {}
            self.good = False
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
                    cMain = chr(nMain)
                    if cMain in puas:
                        privates.add(cMain)
                        continue
                    if cMain == chr(0):
                        continue
                    second = None
                    rest = rest.replace(" ", "")
                    if rest:
                        if HEX_RE.match(rest):
                            second = rest.lower()
                    if second:
                        nSecond = int(second, base=16)
                        cSecond = chr(nSecond)
                        if nSecond > nMain:
                            doubles[cMain] = cSecond
                        else:
                            doubles[cSecond] = cMain

    def showChar(self, c):
        if c in {1, 2}:
            return f"""
<div class="ch p">
    <div class="cn">{LETTER_KIND[c]}</div>
</div>
"""

        puas = self.puas
        rls = self.rls

        ccode = f"""<span class="{"p" if c in puas else "c"}">{ord(c):>04x}</span>"""
        crep = (
            "??" if c in puas else f"""<span class="{"rc" if c in rls else "lc"}">{c}"""
        )
        cname = "" if c in puas else f"""<span class="c">{uName(c)}</span>"""

        return f"""
<div class="ch">
    <div class="cn">{ccode}</div>
    <div class="cn"><span class="cni">{crep}</span></div>
    <div class="cn">{cname}</div>
</div>
"""

    def plainChar(self, c):
        if c == "":
            return "⌊⌋"
        if c in {1, 2}:
            return CODE_LETTER[c]
        return f"⌊{ord(c):>04x}⌋"

    def showString(self, s, asString=False):
        display(HTML(f"""<p><span class="r">{s}</span></p>"""))
        html = """<div class="sr">""" + (
            "".join(self.showChar(c) for c in s) + "</div>"
        )
        if asString:
            return html
        display(HTML(html))

    def plainString(self, s):
        return " ".join(self.plainChar(c) for c in s)

    def showReplacements(self):
        ruleIndex = self.ruleIndex
        rulesApplied = self.rulesApplied

        html = []
        html.append("<table>")

        for (rn, applied) in sorted(
            rulesApplied.items(), key=lambda x: (-sum(x[1].values()), x[0])
        ):
            (vals, d, repls, e) = ruleIndex[rn]

            valRep = "".join(self.showChar(c) for c in vals)
            replRep = "".join(self.showChar(c) for c in repls)
            total = sum(applied.values())
            if applied:
                examplePageNum = sorted(applied, key=lambda p: -applied[p])[0]
                nExamples = applied[examplePageNum]
                appliedEx = f"e.g. page {examplePageNum} with {nExamples} applicaitons"
            else:
                appliedEx = ""
            appliedRep = f"<b>{total}</b> x applied on <i>{len(applied)}</i> pages"
            html.append(
                f"""
<tr>
    <th>rule {rn}</th>
    <td>{appliedRep}</td>
    <td>{appliedEx}</td>
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

    def getPages(self, pageNumSpec, refreshConfig=False):
        if not self.good:
            print("SKIPPING because of config errors")
            return

        ruleIndex = self.ruleIndex
        rulesApplied = self.rulesApplied

        if refreshConfig:
            self.getCharConfig()

        for rn in ruleIndex:
            rulesApplied[rn] = collections.Counter()

        for (i, pageNum) in enumerate(self.parsePageNums(pageNumSpec)):
            self.pageNum = pageNum
            rep = (
                f"{i + 1:>4} (page {pageNum:>4})"
                if pageNum != i + 1
                else (f"{i + 1:>4}" + " " * 12)
            )
            sys.stdout.write(f"\r\t{rep}")
            sys.stdout.flush()
            doc = self.doc
            page = doc[pageNum - 1]

            textPage = page.getTextPage()
            data = textPage.extractRAWDICT()
            self.collectPage(data)
        print("")

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

    def showLines(self, pageNumSpec, line=None, start=None, end=None, search=None):
        lines = self.lines
        pageNums = self.parsePageNums(pageNumSpec)
        lineNums = parseNums(line)

        myLines = {pageNum: lines[pageNum] for pageNum in pageNums if pageNum in lines}

        html = []
        html.append("<table>")
        html.append(
            """
<tr>
    <th>seq</th>
    <th>top</th>
    <th>bottom</th>
    <th>left</th>
    <th>right</th>
    <th>spacing</th>
    <th>font</th>
    <th>size</th>
    <th>orig char</th>
    <th>char</th>
</tr>
"""
        )

        shift = 5
        found = False

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
                pos = None
                if search is not None:
                    pos = -1
                    for (i, char) in enumerate(chars):
                        if char[-2] == search:
                            pos = i
                            found = True
                            break

                if pos is None:
                    occStart = 0
                    occEnd = nChars
                elif pos == -1:
                    continue
                else:
                    occStart = max((pos - shift, 0))
                    occEnd = min((pos + shift + 1, nChars))
                for (i, char) in enumerate(chars):
                    if (
                        start is not None
                        and i + 1 < start
                        or end is not None
                        and i + 1 > end
                    ):
                        continue
                    if i < occStart or i >= occEnd:
                        continue
                    (le, to, ri, bo, font, size, spacing, oc, c) = char
                    html.append(
                        f"""
<tr>
    <td><b>{i + 1}</b></td>
    <td>{ptRep(to)}</td>
    <td>{ptRep(bo)}</td>
    <td>{ptRep(le)}</td>
    <td>{ptRep(ri)}</td>
    <td>{spacing}</td>
    <td>{font}</td>
    <td>{size}pt</td>
    <td>{"".join(self.showChar(x) for x in oc)}</td>
    <td>{"".join(self.showChar(x) for x in c)}</td>
</tr>
"""
                    )
                if found:
                    break

        html.append("</table>")
        display(HTML("".join(html)))

    def showUsedChars(self, pageNumSpec, onlyPuas=False, long=False, byOcc=False):
        pageNums = self.parsePageNums(pageNumSpec)
        text = self.text

        charsOut = collections.defaultdict(collections.Counter)

        def keyByOcc(c):
            pageNums = charsOut[c]
            return -sum(pageNums.values())

        sortKey = keyByOcc if byOcc else lambda x: x

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

        for c in sorted(charsOut, key=sortKey):
            pageNums = charsOut[c]
            nPageNums = len(pageNums)
            pageRep = "page" + ("" if nPageNums == 1 else "s")
            thistotal = sum(pageNums.values())
            examplePageNum = sorted(pageNums, key=lambda p: -pageNums[p])[0]
            nExamples = pageNums[examplePageNum]
            html.append(
                f"""
<tr>
    <td>{self.showChar(c)}</td>
    <td><b>{thistotal}</b> on <i>{nPageNums}</i> {pageRep}</td>
    <td>e.g. page {examplePageNum} with <b>{nExamples}</b> occurrences</td>
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

    def collectPage(self, data):
        doubles = self.doubles
        pageNum = self.pageNum
        nospacings = self.nospacings

        chars = []
        prevChar = None
        prevFont = None
        prevSize = None

        def addChar():
            box = prevChar["bbox"]
            c = prevChar["c"]
            chars.append(
                (
                    *box,
                    prevFont,
                    prevSize,
                    "" if c in nospacings else True,
                    c,
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
                    skip = False
                    if c == " ":
                        skip = True

                    if prevChar is not None:
                        pc = prevChar["c"]
                        if pc in doubles and doubles[pc] == c:
                            skip = True
                        if c in doubles and doubles[c] == pc:
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
        for char in sorted(chars, key=lambda c: (clusterKeyCharV(c), keyCharH(c))):
            k = clusterKeyCharV(char)
            lines.setdefault(k, []).append(list(char))

        self.lines[pageNum] = tuple(lines.values())
        self.text[pageNum] = tuple(
            self.trimLine(pageNum, ln + 1, line)
            for (ln, line) in enumerate(self.lines[pageNum])
        )

    def trimLine(self, pageNum, ln, chars):
        """Map character sequences to other sequences.

        Two tasks:

        1. Map private use characters to well-known unicode characters
        2. Insert space characters where the next character is separated from the
           previous one.

        Complications:

        Diacritical characters are mostly contained in a very wide box that overlaps
        with the boxes of the other characters. So the diacritical boxes must not be
        taken into account.

        Private use characters often com in sequences, so a sequence of characters
        must be transformed to another sequence.

        We do the tramsformation before the space insertion, because otherwise we
        might insert the space at the wrong point.

        When we transform characters we need to retain the box information,
        because we still have to insert the space.

        That's why we have as input a list of character records, where each record
        is itself a list with box information, orginal character, modified characters
        and space information.

        When we transform characters, we modify character records in place.
        We do not add or remove character records.

        The last member of a character record is the modified sequence.
        This can be zero, one, or multiple characters.
        The second last member is the original character.
        Initially, the the last and second last member of each record are equal.
        We call these members the original character and the result string.

        Space will be appended at the last member of the appropriate character records.

        The transformations are given as a set of rules.
        A rule consists of a sequence of characters to match and a sequence of
        characters to replace the match with. We call them the match sequence and the
        replacement sequence of the rule.

        For each character in the input list we check which rules have a match sequence
        that start with this character.
        Of these rules, we start with the one with the longest match sequence.
        We then check, by looking ahead, whether the whole match sequence matches the
        input.
        For the purposes of matching, we look into the result strings of the character,
        not to the original characters. This will prevent some rules to be applied
        after an earlier rule has been applied. This is intentional, and results
        in a more simple rule set.

        If there is a match, we walk through all the characters in the input for the
        length of the match sequence of the rule.
        For each input character record, we set its replacement string to the
        corresponding member of the replacement sequence of the rule.
        If the replacement sequence has run out, we replace with the empty string.
        If after this process the replacement sequence has not been exhausted,
        we join the remaining characters in the replacement string and append it
        after the replacement string of the last input character that we have visited.

        After succesful application of a rule, we do not apply other rules that would
        have been applicable at this point. Instead, we move our starting point to the
        next character record in the sequence and repeat the matching process.

        It might be that a character is replaced multiple times, for example when
        it is reached by a rule while looking ahead 3 places, and then later by a
        different rule looking ahead two places.

        However, once a character matches the first member of the match sequence of
        a rule, and the rule matches and is applied, that character will not be
        changed anymore by any other rule.

        The match sequence may contain the character `d`, which is a placeholder
        for a diacritic sign. It will match any diacritic.
        The replacement sequence of such a rule may or may not contain a `d`.
        It is an error if the replacement seqience of a rule contains a `d` while
        its match sequence does not.
        It is also an error of there are multiple `d`s in a match sequence
        of a replacement sequence.
        If so, the working of this rule is effectively two rules:

        Suppose the rule is

        x d y => r d s

        where x, y, r, s are sequences of arbitrary length.
        If the rule matches the input, then first the rule

        x => r

        will be applied at the current position.

        Then we shift temporarily to the position right after where the d has matched,
        and apply the rule

        y => s

        Then we shift back to the orginal position plus one, and continue applying
        rules.
        """

        replace = self.replace
        puas = self.puas
        neutrals = self.neutrals
        rls = self.rls
        rulesApplied = self.rulesApplied
        diacritics = self.diacritics
        arabicLetters = self.arabicLetters

        nChars = len(chars)

        # rule application stage

        for (i, char) in enumerate(chars):
            c = char[-1]

            if c in replace:
                rules = replace[c]
                for (rn, vals, d, repls, e) in rules:

                    nVals = len(vals)

                    if i + nVals > nChars:
                        # not enough characters left to match this rule
                        continue

                    if not all(
                        (
                            d is not None
                            and j == d
                            and chars[i + j][-1]
                            in (diacritics if vals[d] == 1 else arabicLetters)
                        )
                        or chars[i + j][-1] == vals[j]
                        for j in range(nVals)
                    ):
                        # the rule does not match after all
                        continue

                    # the rule matches: we are going to fill in the replacements
                    # if there is a diacritic in the match sequence or the
                    # replacement sequence, we restrict ourselves to the parts
                    # before the diacritics.

                    rulesApplied[rn][pageNum] += 1

                    nRepls = len(repls)
                    dEnd = nVals if d is None else d
                    eEnd = nRepls if e is None else e

                    # so, we are going to replace from here to dEnd (not including)

                    for j in range(dEnd):
                        # put the appropriate replacement character in the
                        # replacement part of the character record
                        # After running out of replacement characters, put in ""
                        chars[i + j][-1] = repls[j] if j < eEnd else ""

                    if eEnd > dEnd:
                        # if there are replacement characters left, put them
                        # in after the last character that we have visited.

                        if dEnd == 0:
                            # In case we have not visited any yet,
                            # we put them in before the current character
                            cd = chars[i + dEnd][-1]
                            r = "".join(repls[dEnd + 1 :])
                            chars[i + dEnd][-1] = f"{r}{cd}"
                        else:
                            # this is the normal case
                            chars[i + dEnd - 1][-1] += "".join(repls[dEnd:eEnd])

                    # if there is a diacritic in the match sequence
                    # we are going to perform the rule for the part
                    # after the diacritic

                    # Note that the case where d is None and e is not None
                    # does not occur

                    if d is not None:
                        # we set the starting points: just after the diacritics
                        dStart = d + 1
                        # if the replacement part does not have a diacritic,
                        # we have already consumed it, and we start right after it
                        eStart = nRepls if e is None else e + 1

                        # we compute the number of characters that still need to be
                        # matched and to be replaced
                        dn = nVals - dStart
                        en = nRepls - eStart

                        # we perform the replacement analogously to what we did
                        # for the first part

                        for j in range(dn):
                            # put the appropriate replacement character in the
                            # replacement part of the character record
                            # After running out of replacement characters, put in ""
                            chars[i + dStart + j][-1] = (
                                repls[eStart + j] if eStart + j < nRepls else ""
                            )
                        if en > dn:
                            # if there are replacement characters left, put them
                            # in after the last character that we have visited.
                            chars[i + nVals - 1][-1] += "".join(repls[eStart + dn :])
                    break

        prevLeft = None
        prevLeftI = None

        for (i, char) in enumerate(chars):
            spacing = char[-3]

            if spacing:
                left = char[0]
                right = char[2]

                if prevLeft is not None:
                    prevChar = chars[prevLeftI]
                    after = prevLeft - right
                    if after >= 2.5:
                        chars[i - 1][-1] += " "
                        prevChar[-3] = f"⌊{ptRep(after)}⌋"
                    else:
                        prevChar[-3] = f"«{ptRep(after)}»"
                prevLeft = left
                prevLeftI = i

        if chars:
            chars[-1][-3] = "end"

        result = []
        prevDir = "r"
        outChars = []

        def addChars():
            if outChars:
                charsRep = "".join(outChars if prevDir == "r" else reversed(outChars))
                result.append((prevDir, charsRep))

        for char in chars:
            c = char[-1]
            if c == "":
                continue

            for d in c:
                thisDir = prevDir if d in neutrals else "r" if d in rls else "l"

                if prevDir != thisDir:
                    addChars()
                    outChars = []
                    prevDir = thisDir

                rep = d
                if d in puas:
                    rep = f"""⌊{ord(d):>04x}⌋"""
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
    return (char[3] + char[1]) / 2


def keyCharH(char):
    return (-int(round(char[2])), int(round(char[0])))


def clusterVert(data):
    keys = collections.Counter()
    for char in data:
        k = keyCharV(char)
        keys[k] += 1

    peaks = sorted(keys)
    if len(peaks) > 1:
        nDistances = len(peaks) - 1
        avPeakDist = (
            sum(peaks[i + 1] - peaks[i] for i in range(nDistances)) / nDistances
        )

        peakThreshold = avPeakDist / 3
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
