"""Single page processing.
"""

import os
import cv2
import numpy as np
from IPython.display import HTML, display

from .lib import (
    showImage,
    cluster,
    connected,
    removeSkewStripes,
    splitext,
    parseStages,
    parseBands,
)


class Page:
    def __init__(self, engine, f, batch=False, boxed=True):
        """All processing steps for a single page.

        Parameters
        ----------
        engine: object
            The `pipeline.book.Book` object
        f: string
            The file name of the scanned page with extension, without directory
        batch: boolean, optional `False`
            Whether to run in batch mode.
            In batch mode everything is geared to the final output.
            Less intermediate results are computed and stored.
            Less feedback happens on the console.
        boxed: boolean, optional `True`
            If in batch mode, produce also images that display the cleaned marks
            in boxes.
        """

        self.engine = engine
        C = engine.C
        tm = engine.tm
        error = tm.error
        self.file = f
        (self.bare, self.ext) = splitext(f)
        self.empty = True
        self.batch = batch
        self.boxed = boxed
        self.stages = {}
        self.bands = {}

        inDir = C.inDir
        path = f"{inDir}/{f}"
        if not batch and not os.path.exists(path):
            error(f"Page file not found: {path}")
            return

        self.empty = False
        orig = cv2.imread(path)

        self.stages = {"orig": orig}

    def show(self, stage=None, **displayParams):
        """Displays processing stages of an page.

        See `pipeline.parameters.STAGE_ORDER`.

        Parameters
        ----------
        stage: string | iterable, optional `None`
            If no stage is passed, all stages are shown as thumbnails.
            Otherwise, the indicated stages are shown.
            If a string, it may be a comma-separated list of stage names.
            Otherwise it is an iterable of stage names.
        display: dict, optional
            A set of display parameters, such as `width`, `height`
            (anything accepted by `IPython.display.Image`).
        """

        engine = self.engine
        tm = engine.tm
        error = tm.error
        C = engine.C

        stages = self.stages

        for s in parseStages(stage, set(stages), C.stageOrder, error):
            display(HTML(f"<div>{s}</div>"))
            showImage(stages[s], **displayParams)

    def write(self, stage=None):
        """Writes processing stages of an page to disk.

        Parameters
        ----------
        stage: string | iterable, optional `None`
            If no stage is passed, all stages are shown as thumbnails.
            Otherwise, the indicated stages are shown.
            If a string, it may be a comma-separated list of stage names.
            Otherwise it is an iterable of stage names.

        Returns
        -------
            The stages are written into the `inter` subdirectory,
            with the name of the stage appended to the file name.
        """

        engine = self.engine
        tm = engine.tm
        error = tm.error
        C = engine.C
        interDir = C.interDir

        bare = self.bare
        ext = self.ext
        stages = self.stages

        for s in parseStages(stage, C.stages, C.stageOrder, error):
            if s not in stages:
                continue
            img = stages[s]
            path = f"{interDir}/{bare}-{s}.{ext}"
            cv2.imwrite(path, img)

    def normalize(self):
        """Normalizes a page.

        It produces a stage that is unskewed: *rotated* and blurred.
        The same rotation will be applied to the original scan,
        resulting in stage *normalized*.

        Unskewing is needed otherwise the footnote line will not be found.
        """

        if self.empty:
            return

        engine = self.engine
        C = engine.C

        batch = self.batch
        boxed = self.boxed
        stages = self.stages
        orig = stages["orig"]

        removeSkewStripes(orig, C.skewBorder, C.whiteRGB)
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        stages["gray"] = gray

        blurred = cv2.GaussianBlur(gray, (C.blurX, C.blurY), 0, 0)

        (th, threshed) = cv2.threshold(
            blurred, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )
        pts = cv2.findNonZero(threshed)
        ret = cv2.minAreaRect(pts)

        (cx, cy), (rw, rh), ang = ret
        if rw > rh:
            rw, rh = rh, rw
            ang += 90

        M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)

        rotated = cv2.warpAffine(threshed, M, (threshed.shape[1], threshed.shape[0]))
        removeSkewStripes(rotated, C.skewBorder, C.blackRGB)
        normalized = cv2.warpAffine(gray, M, (gray.shape[1], gray.shape[0]))
        removeSkewStripes(normalized, C.skewBorder, C.whiteGRS)

        if not batch or boxed:
            normalizedC = cv2.warpAffine(orig, M, (orig.shape[1], orig.shape[0]))
            removeSkewStripes(normalizedC, C.skewBorder, C.whiteRGB)
            stages["normalizedC"] = normalizedC

        stages["rotated"] = rotated
        stages["normalized"] = normalized

    def histogram(self):
        """Add histograms to a page.

        A new stage of the page, *histogram*, is added.

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

    def margins(self):
        """Chop off margins of an page.

        A new stage of the page, *demargined*, is added.

        !!! caution "it is assumed that the page has a histogram"
            This method uses the histogram info of the page.
        """

        if self.empty:
            return

        engine = self.engine
        C = engine.C

        batch = self.batch
        boxed = self.boxed
        dividers = engine.dividers

        threshold = C.marginThreshold
        mcolor = C.marginRGB

        stages = self.stages
        normalized = stages["normalized"]
        demargined = normalized.copy()
        if not batch or boxed:
            normalizedC = stages["normalizedC"]
            demarginedC = normalizedC.copy()

        histX = self.histX
        histY = self.histY

        (normH, normW) = normalized.shape[:2]
        for pixel in range(0, normW):
            if histX[pixel] < threshold:
                cv2.line(demargined, (pixel, 0), (pixel, normH), mcolor, 1)
                if not batch or boxed:
                    cv2.line(demarginedC, (pixel, 0), (pixel, normH), mcolor, 1)

        uppers = []
        lowers = []

        inline = False
        detectedUpper = False
        detectedLower = False

        for y in range(normH - 1):
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

        footnoteMark = dividers.get("footnote", {}).get("gray", None)
        footnoteFound = (False, None, 100)

        if footnoteMark is not None:
            (divh, divw) = footnoteMark.shape[:2]
            for (i, (upper, lower)) in enumerate(zip(uppers, lowers)):
                roi = normalized[upper - 10 : lower + 10, 10 : normW - 10]
                (roih, roiw) = roi.shape[:2]
                if roih < divh or roiw < divw:
                    # divider template exceeds roi image
                    continue
                result = cv2.matchTemplate(roi, footnoteMark, cv2.TM_CCOEFF_NORMED)
                loc = np.where(result >= 0.5)
                if loc[0].size:
                    footnoteFound = (True, roi, int(round(100 * uppers[i] / normH)))
                    cv2.rectangle(
                        demargined, (0, uppers[i]), (normW, normH), mcolor, -1
                    )
                    if not batch or boxed:
                        cv2.rectangle(
                            demarginedC, (0, uppers[i]), (normW, normH), mcolor, -1
                        )
                    break
                else:
                    continue
            # lastLine = i if footnoteFound[0] else i + 1
            lastLine = i + 1
            uppers = uppers[0:lastLine]
            lowers = lowers[0:lastLine]
        self.dividers = dict(footnote=footnoteFound)

        offsetBand = C.offsetBand
        colorBand = C.colorBand

        bands = {}
        self.bands = bands

        bands["main"] = dict(uppers=uppers, lowers=lowers)
        for (band, bandColor) in colorBand.items():
            (top, bottom) = offsetBand[band]
            isInter = band in {"inter", "low", "high"}
            theUppers = tuple(x + top for x in (lowers[:-1] if isInter else uppers))
            theLowers = tuple(x + bottom for x in (uppers[1:] if isInter else lowers))
            if band not in {"inter", "low"}:
                theUppers = theUppers[0:-1]
                theLowers = theLowers[0:-1]
            bands[band] = dict(uppers=theUppers, lowers=theLowers, color=bandColor)

        # remove top white space

        broadBand = bands["broad"]
        broadUppers = broadBand["uppers"]
        if broadUppers:
            top = broadUppers[0]
            cv2.rectangle(demargined, (0, 0), (normW, top), mcolor, -1)
            if not batch or boxed:
                cv2.rectangle(demarginedC, (0, 0), (normW, top), mcolor, -1)

        self.stages["demargined"] = demargined
        if not batch or boxed:
            self.stages["demarginedC"] = demarginedC

        # show bands

    def showBands(self, stage, showBand, **kwargs):
        engine = self.engine
        tm = engine.tm
        error = tm.error

        bands = self.bands
        stages = self.stages
        if stage not in stages:
            error(f"No stage {stage}")
            return
        img = stages[stage].copy()
        imW = img.shape[1]

        doBands = parseBands(showBand, set(bands), error)

        for band in doBands:
            bandInfo = bands[band]
            uppers = bandInfo["uppers"]
            lowers = bandInfo["lowers"]
            bColor = bandInfo["color"]
            for (upper, lower) in zip(uppers, lowers):
                cv2.rectangle(img, (10, upper), (imW - 10, lower), bColor, 2)
                cv2.rectangle(img, (0, upper), (10, lower), bColor, -1)
                cv2.rectangle(img, (imW - 10, upper), (imW, lower), bColor, -1)
        display(HTML(f"<div>{', '.join(doBands)}</div>"))
        showImage(img, **kwargs)

    def clean(self, mark=None, line=None):
        """Remove marks from the page.

        The page is cleaned of marks.

        New stages of the page are added:

        *   *clean* all targeted marks removed
        *   *cleanh* all targeted marks highlighted in light gray
        *   *boxed* all targeted marks boxed in light gray

        Parameters
        ----------
        marks: iterable of tuples (band, mark, [params]), optional `None`
            If `None`, all non-divider marks that are presented in the book
            directory are used.
            Otherwise, a series of marks is specified together with the band
            where this mark is searched in. Optionally you can also
            put parameters in the tuple: the accuracy and the connectBorder.
        """

        if self.empty:
            return

        engine = self.engine
        tm = engine.tm
        indent = tm.indent
        info = tm.info
        error = tm.error
        warning = tm.warning
        C = engine.C

        marks = engine.marks
        batch = self.batch
        boxed = self.boxed

        boxDelete = C.boxDeleteRGB
        boxRemain = C.boxRemainRGB
        boxBorder = C.boxBorder

        connectBorder = C.connectBorder
        threshold = C.connectThreshold
        ratio = C.connectRatio
        maxHits = C.maxHits
        color = dict(clean=C.cleanRGB, cleanh=C.cleanhRGB,)

        if mark is None:
            searchMarks = {
                subdir: markItems
                for (subdir, markItems) in marks.items()
                if subdir != "divider"
            }
        else:
            for item in mark:
                (band, name) = item[0:2]
                if band == "divider":
                    error("No dividers allowed for cleaning")
                    continue
                if band not in marks or name not in marks[band]:
                    error(f"No such mark: {band}/{mark}")
                    continue
                markParams = item[2] if len(mark) > 2 else {}
                configuredMark = marks[band][mark]
                searchMarks.setdefault(band, {})[mark] = dict(
                    gray=configuredMark["gray"]
                )
                for k in ("accuracy", "connectBorder"):
                    searchMarks[band][mark][k] = markParams.get(k, configuredMark[k])

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

        for (band, markData) in searchMarks.items():
            for (markName, markInfo) in markData.items():
                markInfoName = f"{band}.{markName}"
                foundHits[markInfoName] = 0
                mark = markInfo["gray"]
                connectBorder = markInfo["connectBorder"]
                accuracy = markInfo["accuracy"]
                (markH, markW) = mark.shape[:2]
                bandData = bands[band]
                uppers = bandData["uppers"]
                lowers = bandData["lowers"]
                nPts = 0
                clusters = []
                if not batch:
                    cInfo[markInfoName] = {}
                    einfo = cInfo[markInfoName]
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
                    if roih < markH or roiw < markW:
                        # search template exceeds roi image
                        continue
                    if line is not None:
                        showImage(roi)
                    result = cv2.matchTemplate(roi, mark, cv2.TM_CCOEFF_NORMED)
                    loc = np.where(result >= accuracy)
                    pts = list(zip(*loc))
                    if len(pts) > maxHits:
                        error(
                            f"mark '{markInfoName}':"
                            f" too many hits: {len(pts)} > {maxHits}"
                        )
                        warning(f"Increase accuracy for this template")
                        continue
                    if not pts:
                        continue

                    nPts += len(pts)
                    clusters = cluster(pts, result)

                    for (pt, bestValue) in clusters:
                        connDegree = connected(
                            markH, markW, connectBorder, threshold, roi, pt
                        )
                        pt = (pt[0] + upper, pt[1])
                        if not batch:
                            hits.append(
                                dict(accuracy=bestValue, conn=connDegree, point=pt)
                            )
                        hit = (
                            (pt[1], pt[0]),
                            (pt[1] + markW, pt[0] + markH),
                        )
                        if connDegree > ratio:
                            if not batch or boxed:
                                cv2.rectangle(
                                    stages["boxed"], *hit, boxRemain, boxBorder
                                )
                        else:
                            foundHits[markInfoName] += 1
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

        for markInfoName in sorted(cInfo):
            einfo = cInfo[markInfoName]
            totalHits = len(einfo["hits"])
            if not totalHits:
                continue
            connectBorder = einfo["border"]
            ratio = einfo["ratio"]
            showImage(engine.marks[markInfoName]["gray"])
            connHits = len([hit for hit in einfo["hits"] if hit["conn"] > ratio])
            realHits = totalHits - connHits
            total += realHits
            info(
                f"{markInfoName:<20} with border {connectBorder}:\n"
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
