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

from IPython.display import display, HTML

from kraken.lib.util import array2pil, pil2array
from kraken.lib.models import load_any
from kraken.binarization import nlbin
from kraken.rpred import rpred

from tf.core.helpers import unexpanduser


RL = "horizontal-rl"
TEMPLATE = dict(
    line="""\
<div
    class="l"
    style="
        left: «left»px;
        top: «top»px;
        width: «width»px;
        height: «height»px;
    "
>
    <span class="n">«text»</span>
</div>
""",
    word="""\
<div
    class="w"
    style="
        left: «left»px;
        top: «top»px;
        width: «width»px;
        height: «height»px;
        background-color: «background»;
    "
>
    <span class="a">«text»</span>
</div>
""",
    char="""\
<div
    class="c"
    style="
        left: «left»px;
        top: «top»px;
        width: «width»px;
        height: «height»px;
        background-color: «background»;
    "
>
    <span class="b">«text»</span>
</div>
""",
    doc="""\
<html>
  <head>
  <meta charset="utf-8"/>
<style>
body {
  position: absolute;
  width: «width»px;
  height: «height»px;
}
div.page {
  position: absolute;
  width: «width»px;
  height: «height»px;
}
.img {
  position: absolute;
  width: «width»px;
}
.l {
  position: absolute;
  border-color: hsla(180, 100%, 50%, 0.3);
  border-width: 4px;
  border-style: solid;
  text-align: left;
}
.w {
  position: absolute;
  border-color: hsla(180, 100%, 50%, 0.5);
  border-width: 2px;
  border-style: solid;
  border-top-style: none;
}
.c {
  position: absolute;
  border-color: hsla(180, 100%, 50%, 0.7);
  border-width: 1px;
  border-style: solid;
  border-top-style: none;
  text-align: right;
}
.n {
  position: absolute;
  right: -1em;
  font-family: sans-serif;
  font-size: medium;
  color: #4400bb;
  vertical-align: top;
}
.a {
  position: absolute;
  top: -10px;
  right: 0px;
  font-family: Arial;
  font-size: x-large;
  color: #4400bb;
  vertical-align: top;
}
.b {
  position: absolute;
  top: -10px;
  right: 0px;
  font-family: Arial;
  font-size: large;
  color: #4400bb;
  vertical-align: top;
}
</style>
  </head>
<body>
  <div class="page">
    <img class="img" style="left: 0; top: 0;" src="«source»">
    «lines»
    «boxes»
  </div>
</body>
</html>
""",
)


CONF_COLOR = (
    (0, 50, 0, 10, 30, 40, 0.6, 0.6),
    (50, 80, 10, 30, 40, 50, 0.6, 0.5),
    (80, 100, 30, 90, 50, 60, 0.5, 0.3),
    (90, 100, 90, 120, 60, 70, 0.3, 0.1),
)


def getProofColor(conf, test=False):
    for (
        fromConf,
        toConf,
        fromHue,
        toHue,
        fromLight,
        toLight,
        fromOpacity,
        toOpacity,
    ) in CONF_COLOR:
        if conf > toConf:
            continue
        spread = toConf - fromConf
        slopeHue = (toHue - fromHue) / spread
        slopeOpacity = (toOpacity - fromOpacity) / spread
        slopeLight = (toLight - fromLight) / spread
        excess = conf - fromConf
        hue = fromHue + int(round(excess * slopeHue))
        opacity = fromOpacity + excess * slopeOpacity
        light = fromLight + int(round(excess * slopeLight))
        break
    hsla = f"hsla({hue}, 100%, {light}%, {opacity:.2f})"
    if test:
        display(
            HTML(
                f"""
<p style="background-color: {hsla}; font-family: monospace;">
    conf={conf:>3} ⇒ hue={hue:>3} op={opacity:.2f}
</p>
                """
            )
        )
    return hsla


def showConf(stage, results, label="notes"):
    header = f"""
    <tr>
        <th>item</th>
        <th># of {stage}s</th>
        <th>min</th>
        <th>max</th>
        <th>average</th>
        <th style="text-align: left;">{label}</th>
    </tr>
    """

    rows = [header]
    style = ''' style="background-color: {};"'''
    for (label, n, minC, maxC, totC, notes) in results:
        avC = int(round(totC / n))

        minCol = getProofColor(minC)
        maxCol = getProofColor(maxC)
        avCol = getProofColor(avC)

        minSt = style.format(minCol)
        maxSt = style.format(maxCol)
        avSt = style.format(avCol)

        row = f"""
    <tr>
        <th>{label}</th>
        <td>{n}</td>
        <td{minSt}>{minC}</td>
        <td{maxSt}>{maxC}</td>
        <td{avSt}>{avC}</td>
        <td style="text-align: left;">{notes}</td>
    </tr>
        """
        rows.append(row)

    html = f"""
<table>
{"".join(rows[0:10])}
</table>
"""
    if len(rows) > 10:
        html += f"""
<details>
    <summary>see {len(rows) - 10} more:</summary>
<table>
{header}
{"".join(rows[10:])}
</table>
</details>
        """
    display(HTML(html))


class OCR:
    def __init__(self, engine):
        """Sets up OCR with Kraken."""

        self.engine = engine
        self.model = None

    def ensureLoaded(self):
        if self.model is None:
            engine = self.engine
            C = engine.C
            tm = engine.tm
            info = tm.info
            modelPath = C.modelPath

            info(f"Loading for Kraken: {unexpanduser(modelPath)}")
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                model = load_any(modelPath)
            info("model loaded")

            self.model = model
        return self.model

    def read(self, page):
        """Perfoms OCR with Kraken."""

        stages = page.stages
        scan = stages.get("clean", None)
        if scan is None:
            return None

        model = self.ensureLoaded()

        blocks = page.blocks
        ocrChars = []
        ocrWords = []
        ocrLines = []
        stages["char"] = ocrChars
        stages["word"] = ocrWords
        stages["line"] = ocrLines
        binary = pil2array(nlbin(array2pil(scan)))

        for ((stripe, column), data) in blocks.items():
            (left, top, right, bottom) = data["inner"]
            thisBinary = binary[top:bottom, left:right]
            lines = data["bands"]["main"]["lines"]
            for (ln, (up, lo)) in enumerate(lines):
                lln = ln + 1
                roi = thisBinary[up : lo + 1]
                (b, e, roi) = removeMargins(roi, keep=16)
                ocrLines.append((stripe, column, lln, left + b, top + up, left + e, top + lo))
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
                    ocrChars.append((stripe, column, lln, *pos, conf, c))

                    if c == " " and curWord:
                        ocrWords.append((stripe, column, lln, *addWord(curWord)))
                        curWord = []
                        continue
                    curWord.append((c, pos, conf))
                if curWord:
                    ocrWords.append((stripe, column, lln, *addWord(curWord)))

        page.write(stage="line,word,char")

    def proofing(self, page):
        """Produces an OCR proof page"""

        stages = page.stages

        ocrLines = stages["line"]
        normalized = stages["normalized"]
        (h, w) = normalized.shape[:2]

        scale = 1 if w == 0 else 1000 / w

        def g(m, asStr=True):
            scaledM = m if scale == 1 else int(round(m * scale))
            return str(scaledM) if asStr else scaledM

        page.proofW = g(w, asStr=False)
        page.proofH = g(h, asStr=False)

        linesHtml = "".join(
            TEMPLATE["line"]
            .replace("«left»", g(left))
            .replace("«top»", g(top))
            .replace("«width»", g(right - left))
            .replace("«height»", g(bottom - top))
            .replace("«text»", f"{ln:>01}")
            for (stripe, column, ln, left, top, right, bottom) in ocrLines
        )

        for stage in ("char", "word"):
            stageData = stages.get(stage, [])
            boxesHtml = "".join(
                TEMPLATE[stage]
                .replace("«left»", g(left))
                .replace("«top»", g(top))
                .replace("«width»", g(right - left))
                .replace("«height»", g(bottom - top))
                .replace("«background»", getProofColor(conf))
                .replace("«text»", text)
                for (
                    stripe,
                    column,
                    ln,
                    left,
                    top,
                    right,
                    bottom,
                    conf,
                    text,
                ) in stageData
            )
            proofData = (
                TEMPLATE["doc"]
                .replace("«width»", g(w))
                .replace("«height»", g(h))
                .replace("«source»", page.file)
                .replace("«lines»", linesHtml)
                .replace("«boxes»", boxesHtml)
            )
            proofStage = f"proof{stage}"
            with open(page.stagePath(proofStage), "w") as f:
                f.write(proofData)
            stages[proofStage] = f"see proof at {stage} level"


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
