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

import cv2

from kraken.lib.util import array2pil, pil2array
from kraken.lib.models import load_any
from kraken.binarization import nlbin
from kraken.rpred import rpred

from tf.core.helpers import unexpanduser

from .lib import FONT


RL = "horizontal-rl"
HEADERS = tuple("""
    stripe
    column
    line
    left
    top
    right
    bottom
    confidence
    text
""".strip().split())


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

        for ((stripe, column), data) in blocks.items():
            (left, top, right, bottom) = data["inner"]
            thisBinary = binary[top:bottom, left:right]
            lines = data["bands"]["main"]["lines"]
            for (ln, (up, lo)) in enumerate(lines):
                roi = thisBinary[up : lo + 1]
                (roiH, roiW) = roi.shape[0:2]
                roi = array2pil(roi)
                bounds = dict(boxes=([0, 0, roiW, roiH],), text_direction=RL)

                curLines = []
                for (c, (le, to, ri, bo), conf) in chain.from_iterable(
                    rpred(model, roi, bounds, bidi_reordering=True)
                ):
                    if c == " " and curLines:
                        ocrWords.append((stripe, column, ln, *addWord(curLines)))
                        curLines = []
                        continue
                    offsetW = left
                    offsetH = top + up
                    pos = (le + offsetW, to + offsetH, ri + offsetW, bo + offsetH)
                    conf = int(round(conf * 100))
                    ocrChars.append((stripe, column, ln, *pos, conf, c))
                    curLines.append((c, pos, conf))
                if curLines:
                    ocrWords.append((stripe, column, ln, *addWord(curLines)))

    def proofing(self, page):
        """Produces an OCR proof page"""

        stages = page.stages
        ocrw = stages["ocrw"]
        proof = stages["demarginedC"].copy()
        stages["proof"] = proof
        for (stripe, column, ln, left, top, right, bottom, conf, word) in ocrw:
            markWord(proof, left, top, right, bottom, conf, word)


def addWord(curLines):
    word = "".join(x[0] for x in curLines)
    conf = int(round(sum(x[-1] for x in curLines) / len(curLines)))
    left = min(x[1][0] for x in curLines)
    top = min(x[1][1] for x in curLines)
    right = max(x[1][2] for x in curLines)
    bot = max(x[1][3] for x in curLines)

    return (left, top, right, bot, conf, word)


PROOF_COLORS = {
    100: (0, 200, 0),
    90: (20, 180, 0),
    80: (40, 160, 0),
    70: (60, 140, 0),
    60: (80, 120, 0),
    50: (100, 100, 0),
    40: (120, 80, 0),
    20: (140, 60, 0),
    10: (160, 80, 0),
    0: (180, 20, 0),
}


def markWord(img, left, top, right, bottom, conf, word):
    color = PROOF_COLORS[int(conf // 10) * 10]
    cv2.rectangle(img, (left, top), (right, bottom), color, 2)
    cv2.putText(
        img,
        word,
        (right, top),
        FONT,
        0.7,
        color,
        1,
        cv2.LINE_AA,
    )
