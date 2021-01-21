from unicodedata import name as uname, normalize


NFKC = "NFKC"
NFKD = "NFKD"

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
        self.arabic = getSetFromRanges(ARABIC_RANGES)
        self.hebrew = getSetFromRanges(HEBREW_RANGES)
        self.syriac = getSetFromRanges(SYRIAC_RANGES)
        self.latinPresentational = getSetFromRanges(LATIN_PRESENTATIONAL_RANGES)
        self.greekPresentational = getSetFromRanges(GREEK_PRESENTATIONAL_RANGES)
        self.arabicPresentational = getSetFromRanges(ARABIC_PRESENTATIONAL_RANGES)
        arabicSymbols = getSetFromRanges(ARABIC_SYMBOL_RANGES)
        self.stops = getSetFromRanges(STOP_RANGES)
        self.punct = getSetFromRanges(PUNCT_RANGES) | self.stops
        self.hebrewPresentational = getSetFromRanges(HEBREW_PRESENTATIONAL_RANGES)
        self.presentationalC = self.arabicPresentational | self.hebrewPresentational
        self.presentationalD = self.latinPresentational | self.greekPresentational
        self.presentational = self.presentationalC | self.presentationalD
        self.semis = self.arabic | self.hebrew | self.syriac
        brackets = getSetFromRanges(BRACKET_RANGES)
        symbols = getSetFromRanges(SYMBOL_RANGES)
        self.nonLetter = symbols | arabicSymbols | brackets
        self.bracketMap = getMapFromPairs(BRACKET_PAIRS)
        self.neutrals = getSetFromRanges(NEUTRAL_DIRECTION_RANGES) | brackets | symbols
        self.nospacings = getSetFromRanges(NO_SPACING_RANGES)
        self.diacritics = getSetFromRanges(DIACRITIC_RANGES)
        self.diacriticLike = getSetFromRanges(PSEUDO_DIACRITIC_RANGES) | self.diacritics
        self.arabicLetters = self.arabic - self.diacritics
        self.rls = self.semis
