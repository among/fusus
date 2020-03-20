import os
import cv2
import numpy as np
from IPython.display import HTML, display

from .lib import showImage, cluster, connected, removeSkewStripes, splitext, configure


BLACK_GRS = 0
WHITE_GRS = 255

BLACK_RGB = (0, 0, 0)
WHITE_RGB = (255, 255, 255)
NEAR_WHITE_RGB = (250, 250, 250)

SKEW_BORDER = 30

STAGE_ORDER = """
    orig
    gray
    rotated
    normalized
    normalizedC
    histogram
    demargined
    demarginedC
    boxed
    cleanh
    clean
""".strip().split()

STAGES = set(STAGE_ORDER)

NORMALIZE = dict(blurX=31, blurY=11)

MARGINS = dict(
    color=NEAR_WHITE_RGB,
    threshold=5,
    bands=dict(
        main=dict(isInter=False, color=(40, 40, 40)),
        broad=dict(isInter=False, up=-15, down=10, color=(0, 0, 255)),
        narrow=dict(isInter=False, up=10, down=-5, color=(128, 128, 255)),
        inter=dict(isInter=True, up=5, down=5, color=(255, 200, 200)),
    ),
)

CLEAN = dict(
    color=dict(clean=(255, 255, 255), cleanh=(220, 220, 220)),
    boxDelete=(240, 170, 20),
    boxRemain=(170, 240, 40),
    boxBorder=3,
    connectThreshold=200 * 200,
    connectRatio=0.1,
    connectBorder=4,
    maxHits=5000,
)


class ReadableImage:
    def __init__(self, engine, f, batch=False, boxed=True):
        self.engine = engine
        self.C = engine.C
        C = self.C
        tm = engine.tm
        error = tm.error
        self.file = f
        (self.bare, self.ext) = splitext(f)
        self.empty = True
        self.batch = batch
        self.boxed = boxed
        self.stages = {}
        self.bands = {}

        inDir = C["inDir"]
        path = f"{inDir}/{f}"
        if not batch and not os.path.exists(path):
            error(f"Image file not found: {path}")
            return

        self.empty = False
        orig = cv2.imread(path)
        removeSkewStripes(orig, SKEW_BORDER, WHITE_RGB)
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)

        self.stages = {"orig": orig, "gray": gray}

    def show(self, stage=None, **kwargs):
        """Displays a stage of an image.

        If no stage is passed, all stages are shown as thumbnails.
        """

        engine = self.engine
        tm = engine.tm
        error = tm.error

        stages = self.stages
        doStages = (
            STAGE_ORDER
            if stage is None
            else {stage}
            if type(stage) is str
            else list(stage)
        )
        for s in STAGE_ORDER:
            if s not in doStages:
                continue
            if s not in stages:
                error(f"Unknown stage: {s}")
            img = stages[s]
            display(HTML(f"<div>{s}</div>"))
            showImage(img, **kwargs)

    def layer(self, stage):
        """Returns a stage of an image.
        """

        engine = self.engine
        tm = engine.tm
        error = tm.error
        stages = self.stages

        if stage not in stages:
            diag = "Unknown stage" if stage not in STAGES else "Stage not present"
            error(f"{diag}: {stage}, showing original stage")
            stage = "orig"
        what = stages.get(stage, None)
        if what is None:
            error(f"No stage: orig")
        return what

    def write(self, stage=None):
        """Writes a stage of an image to disk.

        If no stage is passed, all stages are written.
        """

        engine = self.engine
        tm = engine.tm
        error = tm.error
        C = self.C
        interDir = C["interDir"]

        bare = self.bare
        ext = self.ext
        stages = self.stages

        if stage is None:
            for s in STAGE_ORDER:
                if s not in stages:
                    continue
                img = stages[s]
                path = f"{interDir}/{bare}-{s}.{ext}"
                cv2.imwrite(path, img)
            return

        if stage not in stages:
            error(f"Unknown stage: {stage}, writing clean stage")
        what = stages.get(stage, "clean")
        if what is None:
            error(f"No stage: clean")

        path = f"{interDir}/{bare}-{stage}.{ext}"
        cv2.imwrite(path, what)

    def normalize(self, **params):
        """Normalizes an image.

        It produces a stage that is unskewed: *rotated* and blurred.
        The same rotation will be applied to the original image,
        resulting in stage *normalized*.

        Unskewing is needed otherwise the footnote line will not be found.
        """

        if self.empty:
            return

        C = configure(NORMALIZE, params)

        batch = self.batch
        boxed = self.boxed
        stages = self.stages
        orig = stages["orig"]
        gray = stages["gray"]

        blurred = cv2.GaussianBlur(gray, (C["blurX"], C["blurY"]), 0, 0)

        (th, threshed) = cv2.threshold(
            blurred, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )
        pts = cv2.findNonZero(threshed)
        ret = cv2.minAreaRect(pts)

        (cx, cy), (w, h), ang = ret
        if w > h:
            w, h = h, w
            ang += 90

        M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)

        rotated = cv2.warpAffine(threshed, M, (threshed.shape[1], threshed.shape[0]))
        removeSkewStripes(rotated, SKEW_BORDER, BLACK_RGB)
        normalized = cv2.warpAffine(gray, M, (gray.shape[1], gray.shape[0]))
        removeSkewStripes(normalized, SKEW_BORDER, WHITE_GRS)
        if not batch or boxed:
            normalizedC = cv2.warpAffine(orig, M, (orig.shape[1], orig.shape[0]))
            removeSkewStripes(normalizedC, SKEW_BORDER, WHITE_RGB)
            stages["normalizedC"] = normalizedC

        stages["rotated"] = rotated
        stages["normalized"] = normalized

    def histogram(self):
        """Add histograms to an image.

        A new stage of the image, *histogram*, is added.

        The histograms contain an indication of the amount of ink in
        horizontal and in vertical rows.

        The histogram values are preserved as well.
        """

        if self.empty:
            return

        batch = self.batch
        boxed = self.boxed
        stages = self.stages
        rotated = self.stages["rotated"]
        self.histX = cv2.reduce(rotated, 0, cv2.REDUCE_AVG).reshape(-1)
        self.histY = cv2.reduce(rotated, 1, cv2.REDUCE_AVG).reshape(-1)

        if not batch or boxed:
            normalizedC = stages["normalizedC"]
            if not batch:
                histogram = normalizedC.copy()

                for (hist, vert) in ((self.histY, True), (self.histX, False)):
                    for (i, val) in enumerate(self.histY):
                        color = (int(val), int(2 * val), int(val))
                        index = (0, i) if vert else (i, 0)
                        value = (val, i) if vert else (i, val)
                        cv2.line(histogram, index, value, color, 1)
                stages["histogram"] = histogram

    def margins(self, **params):
        """Chop off margins of an image.

        A new stage of the image, *demargined*, is added.

        !!! caution "it is assumed that the image has a histogram"
            This method uses the histogram info of the image.
        """

        if self.empty:
            return

        C = configure(MARGINS, params)

        engine = self.engine
        batch = self.batch
        boxed = self.boxed

        threshold = C["threshold"]
        bandConfig = C["bands"]
        mcolor = C["color"]

        engine = self.engine
        dividers = engine.dividers
        stages = self.stages
        normalized = stages["normalized"]
        demargined = normalized.copy()
        if not batch or boxed:
            normalizedC = stages["normalizedC"]
            demarginedC = normalizedC.copy()

        histX = self.histX
        histY = self.histY

        (h, w) = normalized.shape[:2]
        for pixel in range(0, w):
            if histX[pixel] < threshold:
                cv2.line(demargined, (pixel, 0), (pixel, h), mcolor, 1)
                if not batch or boxed:
                    cv2.line(demarginedC, (pixel, 0), (pixel, h), mcolor, 1)

        uppers = []
        lowers = []

        inline = False
        detectedUpper = False
        detectedLower = False

        for y in range(h - 1):
            if inline:
                if detectedLower:
                    if histY[y] >= threshold:
                        lowers[-1] = y
                    elif histY[y] <= 1:
                        inline = False
                elif histY[y] > threshold and histY[y + 1] <= threshold:
                    lowers.append(y)
                    detectedLower = True
                    detectedUpper = False
                    if histY[y] <= 1:
                        inline = False
            else:
                if histY[y] <= threshold and histY[y + 1] > threshold:
                    if not detectedUpper:
                        inline = True
                        uppers.append(y)
                        detectedUpper = True
                        detectedLower = False

        # look for dividers

        footnoteFound = (False, None, 100)
        footnoteMark = dividers.get("footnote", {}).get("gray", None)
        if footnoteMark is not None:
            (divh, divw) = footnoteMark.shape[:2]
            for (i, (upper, lower)) in enumerate(zip(uppers, lowers)):
                roi = normalized[upper - 10 : lower + 10, 10 : w - 10]
                (roih, roiw) = roi.shape[:2]
                if roih < divh or roiw < divw:
                    # divider template exceeds roi image
                    continue
                result = cv2.matchTemplate(roi, footnoteMark, cv2.TM_CCOEFF_NORMED)
                loc = np.where(result >= 0.5)
                if loc[0].size:
                    footnoteFound = (True, roi, int(round(100 * uppers[i] / h)))
                    cv2.rectangle(demargined, (0, uppers[i]), (w, h), mcolor, -1)
                    if not batch or boxed:
                        cv2.rectangle(demarginedC, (0, uppers[i]), (w, h), mcolor, -1)
                    break
                else:
                    continue
            lastLine = i if footnoteFound[0] else i + 1
            uppers = uppers[0:lastLine]
            lowers = lowers[0:lastLine]
        self.dividers = dict(footnote=footnoteFound)

        bandData = {}
        self.bands = bandData
        bandData["main"] = dict(uppers=uppers, lowers=lowers)
        for (band, params) in bandConfig.items():
            isInter = params["isInter"]
            up = params.get("up", 0)
            down = params.get("down", 0)
            color = params["color"]
            theUppers = tuple(x + up for x in (lowers[:-1] if isInter else uppers))
            theLowers = tuple(x + down for x in (uppers[1:] if isInter else lowers))
            bandData[band] = dict(uppers=theUppers, lowers=theLowers, color=color)

        # remove top white space

        broadBand = bandData["broad"]
        broadUppers = broadBand["uppers"]
        if broadUppers:
            top = broadUppers[0]
            cv2.rectangle(demargined, (0, 0), (w, top), mcolor, -1)
            if not batch or boxed:
                cv2.rectangle(demarginedC, (0, 0), (w, top), mcolor, -1)

        self.stages["demargined"] = demargined
        if not batch or boxed:
            self.stages["demarginedC"] = demarginedC

        # show bands

    def showBands(self, stage, showBands):
        batch = self.batch
        if batch:
            return

        bands = self.bands
        stages = self.stages
        img = stages.get(stage, "gray")
        (h, w) = img.shape[:2]

        for (band, bandInfo) in bands.items():
            if showBands is not None and band not in showBands:
                continue
            uppers = bandInfo["uppers"]
            lowers = bandInfo["lowers"]
            bColor = bandInfo["color"]
            for (upper, lower) in zip(uppers, lowers):
                cv2.rectangle(img, (10, upper), (w - 10, lower), bColor, 2)
                cv2.rectangle(img, (0, upper), (10, lower), bColor, -1)
                cv2.rectangle(img, (w - 10, upper), (w, lower), bColor, -1)

    def clean(self, mark=None, line=None, **params):
        """Remove marks from the image.

        The image is cleaned of a given list of marks.

        New stages of the image are added:

        *   *clean* all targeted marks removed
        *   *cleanh* all targeted marks highlighted in light gray
        *   *boxed* all targeted marks boxed in light gray
        """

        if self.empty:
            return

        C = configure(CLEAN, params)

        engine = self.engine
        marks = engine.marks
        tm = engine.tm
        indent = tm.indent
        info = tm.info
        error = tm.error
        warning = tm.warning
        batch = self.batch
        boxed = self.boxed

        boxDelete = C["boxDelete"]
        boxRemain = C["boxRemain"]
        boxBorder = C["boxBorder"]

        connectBorder = C["connectBorder"]
        threshold = C["connectThreshold"]
        ratio = C["connectRatio"]
        maxHits = C["maxHits"]
        color = C["color"]

        searchMarks = (
            set(marks)
            if mark is None
            else set(mark)
            if type(mark) in {list, tuple}
            else {mark}
            if mark in marks
            else set()
        )

        stages = self.stages
        demargined = stages.get("demargined", stages["gray"])
        if batch:
            resultStages = ("clean", "boxed") if boxed else ("clean",)
            if boxed:
                demarginedC = stages.get("demarginedC", stages["orig"])
        else:
            demarginedC = stages.get("demarginedC", stages["orig"])
            resultStages = ("clean", "cleanh", "boxed")
        for stage in resultStages:
            stages[stage] = (demarginedC if stage == "boxed" else demargined).copy()

        tasks = [
            (
                stage,
                stages[stage],
                None if stage == "boxed" else color[stage],
                boxBorder if stage == "boxed" else -1,
            )
            for stage in resultStages
        ]

        cInfo = {}
        foundHits = {}
        cleanClr = color["clean"]
        bands = self.bands
        imageAsRoi = dict(uppers=[0], lowers=[demargined.shape[0]])

        for markName in searchMarks:
            foundHits[markName] = 0
            markInfo = engine.marks[markName]
            mark = markInfo["gray"]
            band = markInfo["band"]
            connectBorder = markInfo["connectBorder"]
            accuracy = markInfo["accuracy"]
            (h, w) = mark.shape[:2]
            bandData = bands.get(band, imageAsRoi)
            uppers = bandData["uppers"]
            lowers = bandData["lowers"]
            nPts = 0
            clusters = []
            if not batch:
                cInfo[markName] = {}
                einfo = cInfo[markName]
                einfo["hits"] = []
                einfo["connected"] = 0
                einfo["border"] = connectBorder
                einfo["ratio"] = ratio
                hits = einfo["hits"]
            else:
                hits = []
            for (i, (upper, lower)) in enumerate(zip(uppers, lowers)):
                if line is not None:
                    if i < line - 1:
                        continue
                    elif i > line - 1:
                        break
                roi = demargined[
                    upper : lower + 1,
                ]
                (roih, roiw) = roi.shape[:2]
                if roih < h or roiw < w:
                    # search template exceeds roi image
                    continue
                if line is not None:
                    showImage(roi)
                result = cv2.matchTemplate(roi, mark, cv2.TM_CCOEFF_NORMED)
                loc = np.where(result >= accuracy)
                pts = list(zip(*loc))
                if len(pts) > maxHits:
                    error(f"mark '{markName}': too many hits: {len(pts)} > {maxHits}")
                    warning(f"Increase accuracy for this template")
                    continue
                if not pts:
                    continue

                nPts += len(pts)
                clusters = cluster(pts, result)

                for (pt, bestValue) in clusters:
                    connDegree = connected(h, w, connectBorder, threshold, roi, pt)
                    pt = (pt[0] + upper, pt[1])
                    if not batch:
                        hits.append(dict(accuracy=bestValue, conn=connDegree, point=pt))
                    hit = (
                        (pt[1], pt[0]),
                        (pt[1] + w, pt[0] + h),
                    )
                    if connDegree > ratio:
                        if not batch or boxed:
                            cv2.rectangle(stages["boxed"], *hit, boxRemain, boxBorder)
                    else:
                        foundHits[markName] += 1
                        if batch and not boxed:
                            cv2.rectangle(stages["clean"], *hit, cleanClr, -1)
                        else:
                            for (stage, im, clr, brd) in tasks:
                                isBoxed = stage == "boxed"
                                theClr = boxDelete if isBoxed else clr
                                theBrd = boxBorder if isBoxed else -1
                                cv2.rectangle(im, *hit, theClr, theBrd)

            if not batch:
                einfo["npoints"] = nPts
        for (mark, found) in sorted(foundHits.items()):
            indent(level=2)
            if found:
                warning(f"{mark:>20} {found:>4} times", tm=False)
        indent(level=1)
        info("cleaning done")

        self.cleanInfo = cInfo

    def showCleanInfo(self):
        engine = self.engine
        engine = self.engine
        tm = engine.tm
        info = tm.info
        cInfo = self.cleanInfo
        total = 0

        for markName in sorted(cInfo):
            einfo = cInfo[markName]
            totalHits = len(einfo["hits"])
            if not totalHits:
                continue
            connectBorder = einfo["border"]
            ratio = einfo["ratio"]
            showImage(engine.marks[markName]["gray"])
            connHits = len([h for h in einfo["hits"] if h["conn"] > ratio])
            realHits = totalHits - connHits
            total += realHits
            info(
                f"{markName:<12} with border {connectBorder}:\n"
                f" {realHits} hits in {einfo['npoints']} points\n"
                f" {connHits} connected hits removed from {totalHits} candidate hits",
                tm=False,
            )
            for hit in einfo["hits"]:
                conn = hit["conn"]
                ast = "*" if conn > ratio else " "
                info(
                    f"\t{ast}hit"
                    f" with accuracy {hit['accuracy']:5.2f}"
                    f" with connectivity {ast}{hit['conn']:5.2f}"
                    f" reached by {hit['point']}",
                    tm=False,
                )

        info(f"{total} marks wiped clean", tm=False)
