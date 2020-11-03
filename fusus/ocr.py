"""
Kraken Arabic model:

[OpenITI](https://github.com/OpenITI/OCR_GS_Data/blob/master/ara/abhath/arabic_generalized.mlmodel)


We can call Kraken with a batch of images.

We can call binarization and segmentation and ocr in one call, but then
we do not get the line segmentation json file.

So we split it up in three batch calls: one for binarize, one for segmentation,
and one for ocr.

Alternatively, we can do binarization and segmentation in our preprocessing, and
use Kraken for OCR only.
"""
import warnings
from itertools import chain

import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image

from kraken.lib.util import array2pil, pil2array
from kraken.lib.models import load_any
from kraken.binarization import nlbin
from kraken.rpred import rpred

from tf.core.helpers import unexpanduser

import arabic_reshaper
from bidi.algorithm import get_display


RL = "horizontal-rl"
HEADERS = tuple(
    """
    stripe
    column
    line
    left
    top
    right
    bottom
    confidence
    text
""".strip().split()
)

PROOF_COLORS = {
    100: (0, 200, 0),
    90: (20, 180, 0),
    80: (40, 160, 0),
    70: (60, 140, 0),
    60: (80, 120, 0),
    50: (100, 100, 0),
    40: (120, 80, 0),
    30: (140, 60, 0),
    20: (160, 40, 0),
    10: (180, 20, 0),
    0: (200, 0, 0),
    None: (150, 150, 255),
    "": (150, 0, 150),
}


def getProofColor(conf):
    confStep = conf if type(conf) is not int else int(conf // 10) * 10
    return PROOF_COLORS[confStep]


class OCR:
    def __init__(self, engine):
        """Sets up OCR with Kraken."""

        tm = engine.tm
        info = tm.info

        self.engine = engine
        C = engine.C
        modelPath = C.modelPath
        info(f"Loading for Kraken: {unexpanduser(modelPath)}")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            model = load_any(modelPath)
        info("model loaded")

        self.model = model
        self.proofFont = ImageFont.truetype("Arial", 48)
        self.proofFontSmall = ImageFont.truetype("Arial", 32)

    def read(self, page):
        """Perfoms OCR with Kraken."""

        page.dataHeaders["ocr"] = HEADERS
        page.dataHeaders["ocrw"] = HEADERS
        stages = page.stages
        scan = stages.get("clean", None)
        if scan is None:
            return None

        model = self.model

        blocks = page.blocks
        ocrChars = []
        ocrWords = []
        stages["ocr"] = ocrChars
        stages["ocrw"] = ocrWords
        binary = pil2array(nlbin(array2pil(scan)))
        proofLines = []
        self.proofLines = proofLines

        for ((stripe, column), data) in blocks.items():
            (left, top, right, bottom) = data["inner"]
            thisBinary = binary[top:bottom, left:right]
            lines = data["bands"]["main"]["lines"]
            for (ln, (up, lo)) in enumerate(lines):
                roi = thisBinary[up : lo + 1]
                (b, e, roi) = removeMargins(roi, keep=16)
                # print(f"{stripe}{column}:{ln} {left} <-> {right} ~{b} - {e}~ {left + b} <-> {left + e}")
                proofLines.append((ln, left + b, top + up, left + e, top + lo))
                (roiH, roiW) = roi.shape[0:2]
                roi = array2pil(roi)
                bounds = dict(boxes=([0, 0, roiW, roiH],), text_direction=RL)

                # adapt the boxes, because they corresponds to peaks of recognition,
                # not to character extends
                #
                # See https://github.com/mittagessen/kraken/issues/184

                adaptedPreds = []
                for (c, (le, to, ri, bo), conf) in chain.from_iterable(
                    rpred(model, roi, bounds, pad=0, bidi_reordering=True)
                ):
                    if adaptedPreds:
                        prevPred = adaptedPreds[-1]
                        prevEdge = prevPred[1][0]
                    else:
                        prevEdge = roiW
                    correction = int(round((prevEdge - ri) / 2))
                    thisRi = ri + correction
                    if adaptedPreds:
                        adaptedPreds[-1][1][0] -= correction
                    adaptedPreds.append([c, [le, to, thisRi, bo], conf])
                if adaptedPreds:
                    adaptedPreds[-1][1][0] = 0

                # divide into words

                curWord = []

                for (c, (le, to, ri, bo), conf) in adaptedPreds:
                    offsetW = left + b
                    offsetH = top + up
                    pos = (le + offsetW, to + offsetH, ri + offsetW, bo + offsetH)
                    conf = int(round(conf * 100))
                    ocrChars.append((stripe, column, ln, *pos, conf, c))

                    if c == " " and curWord:
                        ocrWords.append((stripe, column, ln, *addWord(curWord)))
                        curWord = []
                        continue
                    curWord.append((c, pos, conf))
                if curWord:
                    ocrWords.append((stripe, column, ln, *addWord(curWord)))

    def proofing(self, page):
        """Produces an OCR proof page"""

        proofFont = self.proofFont
        proofFontSmall = self.proofFontSmall
        stages = page.stages

        proofLines = self.proofLines

        for kind in ("", "w"):
            stage = stages[f"ocr{kind}"]
            img = stages["demarginedC"].copy()
            img[np.where((img < [180, 180, 180]).all(axis=2))] = [180, 180, 180]

            # line boxes
            for (ln, left, top, right, bottom) in proofLines:
                color = getProofColor(None)
                boxIt(img, left - 5, top - 2, right + 5, bottom + 2, color, 1)

            # word/char boxes
            width = 3 if kind == "w" else 1
            for (stripe, column, ln, left, top, right, bottom, conf, item) in stage:
                color = getProofColor(conf)
                boxIt(img, left, top, right, bottom - 5, color, width)
                if kind == "":
                    boxIt(img, left, bottom - 5, right, bottom + 5, color, -1)

            img = Image.fromarray(img)
            draw = ImageDraw.Draw(img)

            # line numbers
            for (ln, left, top, right, bottom) in proofLines:
                color = getProofColor(None)
                putText(draw, proofFont, color, (right + 10, top), "la", f"{ln:>02}")

            # word/char ocr values
            font = proofFont if kind == "w" else proofFontSmall
            for (stripe, column, ln, left, top, right, bottom, conf, item) in stage:
                color = getProofColor("")
                if kind == "w":
                    item = arabic_reshaper.reshape(item)
                    item = get_display(item)
                putText(draw, font, color, (right - 5, top - 10), "ra", item)

            stages[f"proof{kind}"] = np.array(img)


def removeMargins(img, keep=0):
    mask = img < 255
    w = img.shape[1]
    mask0 = mask.any(0)
    (start, end) = (mask0.argmax(), w - mask0[::-1].argmax())
    (start, end) = (max((0, start - keep)), min((w, end + keep)))
    return (start, end, img[:, start:end])


def addWord(curChars):
    word = "".join(x[0] for x in curChars)
    conf = int(round(sum(x[-1] for x in curChars) / len(curChars)))
    left = min(x[1][0] for x in curChars)
    top = min(x[1][1] for x in curChars)
    right = max(x[1][2] for x in curChars)
    bot = max(x[1][3] for x in curChars)

    return (left, top, right, bot, conf, word)


def boxIt(img, left, top, right, bottom, color, width):
    cv2.rectangle(img, (left, top), (right, bottom), color, width)


def putText(draw, font, color, pos, anchor, item):
    colorDarkened = tuple(max(0, c - 40) for c in color) + (127,)
    draw.text(
        pos,
        item,
        font=font,
        fill=colorDarkened,
        align="right",
        anchor=anchor,
    )
