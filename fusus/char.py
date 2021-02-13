"""Character knowledge.

This module collects all character knowledge that we need to parse the
Lakhnawi PDF and makes it available to programs.

It contains definitions for things as character classes,
e.g. *symbols*, *presentational characters*, *punctuation*,
*bracket-like characters*, etc.

See `UChar` below.
"""

import re
from unicodedata import name as uname, normalize


NFKC = "NFKC"
NFKD = "NFKD"

EMSPACE = "\u2003"

PUA_RANGES = (("e000", "f8ff"),)

LATIN_PRESENTATIONAL_RANGES = (("00c0", "024f"), ("1e00", "1eff"), ("fb00", "fb06"))

GREEK_PRESENTATIONAL_RANGES = (("1f00", "1fff"),)

ARABIC_RANGES = (
    ("0600", "06ff"),
    ("0750", "077f"),
    ("08a0", "08ff"),
    ("206a", "206f"),
    ("fb50", "fdc7"),
    ("fdf0", "fdfd"),
    ("fe70", "fefc"),
)
ARABIC_SYMBOL_RANGES = (
    ("060c", "060c"),
    ("061b", "061f"),
    ("fd3e", "fd3f"),
)
STOP_RANGES = (
    ("002e", "002e"),
    ("06d4", "06d4"),
)

PUNCT_RANGES = (
    ("0021", "0021"),
    ("002c", "002c"),
    ("003a", "003b"),
    ("003f", "003f"),
    ("00a1", "00a1"),
    ("00bf", "00bf"),
    ("037e", "037e"),
    ("0387", "0387"),
    ("05c3", "05c3"),
    ("060c", "060c"),
    ("061b", "061b"),
    ("061e", "061f"),
)

ARABIC_PRESENTATIONAL_RANGES = (("fb50", "feff"),)

SYRIAC_RANGES = (
    ("0700", "074f"),
    ("2670", "2671"),
)

HEBREW_RANGES = (
    ("0590", "05ff"),
    ("fb1d", "fb4f"),
)

HEBREW_PRESENTATIONAL_RANGES = (("fb1d", "fb4f"),)

SYMBOL_RANGES = (
    ("0021", "0027"),  # exclamation, prime, dollar, etc
    ("002a", "002f"),  # star, comma, minus, stop, slash
    ("003a", "003b"),  # colon, semicolon
    ("003d", "003d"),  # equals
    ("003f", "0040"),  # question mark, commercial
    ("02b0", "036f"),  # modifiers, combiners, accents
    ("2010", "2017"),  # dashes
    ("201a", "201b"),  # single quotation marks
    ("201e", "201f"),  # double quotation marks
    ("2020", "2029"),  # dagger, bullet, leader, ellipsis
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
    ("2018", "2019"),  # quotation marks directed
    ("201c", "201d"),  # quotation marks directed
    ("2039", "203a"),  # guillemets single
    ("2045", "2046"),  # sqare brackets with quill
    ("204c", "204d"),  # bullets directed
)

BRACKET_PAIRS = (
    ("0028", "0029"),  # parentheses
    ("003c", "003e"),  # less than, greater than
    ("005b", "005d"),  # sq brackets
    ("007b", "007d"),  # braces
    ("00ab", "00bb"),  # guillemets double
    ("2018", "2019"),  # qutation marks directed
    ("201c", "201d"),  # qutation marks directed
    ("2045", "2046"),  # sqare brackets with quill
    ("204c", "204d"),  # bullets directed
)

DIRECTION_RANGES = (
    ("202a", "202e"),  # control writing direction
    ("2066", "2069"),  # control writing direction
)

NEUTRAL_DIRECTION_RANGES = (
    ("0009", "0009"),
    ("0020", "0020"),
    ("002e", "002e"),
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
PSEUDO_DIACRITIC_RANGES = (("0621", "0621"),)

AR_DIGIT_RANGES = (("0660", "0669"),)
EU_DIGIT_RANGES = (("0030", "0039"),)

FINAL_SPACE_CODES = """
    fbfd
    fc32
    fc43
    fc5d
    fc8d
    fc90
    fc94
    fe90
    fe94
    fe96
    fe9a
    fe9e
    fea2
    fea6
    feb2
    feb6
    feba
    febe
    fec2
    fec6
    feca
    fece
    fed2
    fed6
    feda
    fede
    fee2
    fee6
    feea
    fef2
""".strip().split()


def uName(c):
    try:
        un = uname(c)
    except Exception:
        un = "NO NAME"
    return un


def getSetFromCodes(codes):
    result = set()
    for c in codes:
        uc = int(c, base=16)
        result.add(chr(uc))
    return result


def getSetFromRanges(rngs):
    result = set()
    for (b, e) in rngs:
        for uc in range(int(b, base=16), int(e, base=16) + 1):
            result.add(chr(uc))
    return result


ISOLATED = "ISOLATED"
INITIAL = "INITIAL"
FINAL = "FINAL"
ALEF = "ALEF"
ALEF_FINAL = "\ufe8e"
WAW = "\u0648"
LO = "Lo"
ALEFS = {"\u0627", "\u0622", "\u0623", "\u0625", "\u0671"}
WAWS = {"\u0648", "\u0624", "\u0676", ""}
PROCLITICS = ALEFS | WAWS
HYPHENS = {"\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u002d", "\u00ad"}

AR_DIGITS = getSetFromRanges(AR_DIGIT_RANGES)
EU_DIGITS = getSetFromRanges(EU_DIGIT_RANGES)

MEEM = "MEEM"
YEH = "YEH"


def getSetFromDef(defs):
    return {chr(int(item, base=16)) for item in defs.strip().split("\n")}


def getMapFromPairs(pairs):
    result = {}
    for (b, e) in pairs:
        bc = chr(int(b, base=16))
        ec = chr(int(e, base=16))
        result[bc] = ec
        result[ec] = bc
    return result


def normalizeC(x):
    return normalize(NFKC, x)


def normalizeD(x):
    return normalize(NFKD, x)


def isAlefFinal(x):
    return x == ALEF_FINAL


def isMeemOrYeh(x):
    nm = uname(x)
    return MEEM in nm or YEH in x


def isWaw(x):
    return x == WAW


def isArDigit(x):
    return x in AR_DIGITS


def isEuDigit(x):
    return x in EU_DIGITS


class UChar:
    def __init__(self):
        self.puas = getSetFromRanges(PUA_RANGES)
        """Private use character codes as defined by the unicode standard."""

        self.arabic = getSetFromRanges(ARABIC_RANGES)
        """All Arabic unicode characters"""

        self.hebrew = getSetFromRanges(HEBREW_RANGES)
        """All Hebrew unicode characters"""

        self.syriac = getSetFromRanges(SYRIAC_RANGES)
        """All Syriac unicode characters"""

        self.latinPresentational = getSetFromRanges(LATIN_PRESENTATIONAL_RANGES)
        """Ligatures and special letter forms in the Latin script"""

        self.greekPresentational = getSetFromRanges(GREEK_PRESENTATIONAL_RANGES)
        """Ligatures and special letter forms in the Greek script"""

        self.arabicPresentational = getSetFromRanges(ARABIC_PRESENTATIONAL_RANGES)
        """Ligatures and special letter forms in the Arabic script"""

        self.hebrewPresentational = getSetFromRanges(HEBREW_PRESENTATIONAL_RANGES)
        """Ligatures and special letter forms in the Hebrew script"""

        self.presentationalC = self.arabicPresentational | self.hebrewPresentational
        """Ligatures and special letter forms (C)

        These are the ones that are best normalized with `NFKC`: Arabic and Hebrew.
        """

        self.presentationalD = self.latinPresentational | self.greekPresentational
        """Ligatures and special letter forms (D)

        These are the ones that are best normalized with `NFKD`: Latin and Greek.
        """

        self.presentational = self.presentationalC | self.presentationalD
        """Ligatures and special letter forms various scripts"""

        arabicSymbols = getSetFromRanges(ARABIC_SYMBOL_RANGES)
        """Arabic characters that act as symbols.

        E.g. the ornate parentheses (used for Quran quotes).
        """

        symbols = getSetFromRanges(SYMBOL_RANGES)
        """Characters that act as symbols in various scripts."""

        self.stops = getSetFromRanges(STOP_RANGES)
        """Characters that have the function of a full stop in several scripts."""

        self.punct = getSetFromRanges(PUNCT_RANGES) | self.stops
        """Punctuation characters in several scripts."""

        self.semis = self.arabic | self.hebrew | self.syriac
        """Characters in semitic scripts.

        These scripts have a right-to-left writing direction.
        """

        self.rls = self.semis
        """Characters that belong to the right-to-left writing direction.

        Identical with the `UChar.semis` category.
        But the Lakhnawi conversion will insert the private use characters
        to this category.
        """

        brackets = getSetFromRanges(BRACKET_RANGES)
        """Characters used for bracketing.

        Only when they have distinct left and right forms.
        """

        self.bracketMap = getMapFromPairs(BRACKET_PAIRS)
        """Mapping between left and right versions of brackets.

        Due to Unicode algorithms, left and right brackets will be displayed
        flipped when used in right-to-left writing direction.

        !!! caution "hard flipping"
            The Lakhnawi PDF contains brackets that have been hard flipped in order
            to display correctly in rtl direction.
            But after text extraction, we can rely on the Unicode algorithm,
            so we have to unflip these characters.
        """

        nonLetter = symbols | arabicSymbols | brackets
        self.nonLetter = nonLetter
        """Characters that act as symbols.

        More precisely, these are the non letters that we may encounter in
        *Arabic* script, including symbols from other scripts and brackets.
        """

        self.neutrals = getSetFromRanges(NEUTRAL_DIRECTION_RANGES) | brackets | symbols
        """Characters that are neutral with respect to writing direction.

        These are the characters that should not trigger a change in writing direction.
        For example, a latin full stop amidst Arabic characters should not trigger
        a character range consisting of that full stop with ltr writing direction.
        """

        self.nospacings = getSetFromRanges(NO_SPACING_RANGES)
        """Characters that will be ignored when figuring out horizontal white space.

        These are characters that appear to have bounding boxes in the Lakhnawi PDF
        that are not helpful in determining horizontal white space.

        When using this category in the Lakhnawi text extraction, extra characters
        will be added to this category, namely the diacritics in the private use
        area. But this is dependent on the Lakhnawi PDF and the Lakhnawi text
        extraction will take care of this.
        """

        self.diacritics = getSetFromRanges(DIACRITIC_RANGES)
        """Diacritical characters in various scripts."""

        self.diacriticLike = getSetFromRanges(PSEUDO_DIACRITIC_RANGES) | self.diacritics
        """Diacritical characters in various scripts plus the Arabic Hamza 0621."""

        self.arabicLetters = self.arabic - self.diacritics
        """Arabic characters with exception of the Arabic diacritics."""

        self.finalSpace = getSetFromCodes(FINAL_SPACE_CODES)
        """Space insertion triggered by final characters.

        Some characters imply a word-boundary after them.

        Characters marked as "FINAL" by Unicode are candidates, but not all of them
        have this behaviour.
        Here is the exact set of characters after which
        we need to trigger a word boundary.
        """

        nonLetterRange = re.escape("".join(sorted(nonLetter)))

        wordRe = re.compile(
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
        self.wordRe = wordRe
        """Regular expression that matches word stretches and non word stretches.

        When we split strings up into words using spaces, we are left with
        strings that contain letters and punctuation.
        This pattern can be used to separate letters from non-letters in such strings.

        Each time this pattern matches, you either get a string consisting of
        stuff that fits in a word (letters, diacritics, etc.),
        or stuff that does not fit in a word (punctuation, symbols, brackets, etc.).

        The policy is to split each string first on space, and then chunk it into
        chunks that are completely word-like or completely non-word-like.

        We then partition this list of chunks into pairs consisting of a
        word-like chunk followed by a non-word-like chunk.

        If the first chunk is non-word-like, we insert an empty chunk before it.

        If the last chunk is word-like, we insert an empty chunk after it.
        """
