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

from kraken.lib.util import array2pil, pil2array
from kraken.lib.models import load_any
from kraken.rpred import rpred
from kraken.binarization import nlbin

from tf.core.helpers import unexpanduser

RL = "horizontal-rl"


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

        stages = page.stages
        scan = stages.get("clean", None)
        if scan is None:
            return None

        model = self.model

        blocks = page.blocks
        ocrData = {}
        stages["ocr"] = ocrData
        binary = pil2array(nlbin(array2pil(scan)))

        for ((stripe, column), data) in blocks.items():
            thisOcrData = []
            (left, top, right, bottom) = data["inner"]
            thisBinary = binary[top:bottom, left:right]
            lines = data["bands"]["main"]["lines"]
            for (i, (up, lo)) in enumerate(lines):
                roi = thisBinary[up : lo + 1]
                (roiH, roiW) = roi.shape[0:2]
                roi = array2pil(roi)
                bounds = dict(
                    boxes=([0, 0, roiW, roiH],), text_direction="RL"
                )
                ocrLine = list(list(rec) for rec in rpred(model, roi, bounds))
                thisOcrData.append((i, ocrLine))
            ocrData[f"{stripe:>01}-{column}"] = thisOcrData

        return ocrData
