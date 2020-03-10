import sys
import os
import cv2
import numpy as np
from IPython.display import HTML, display

from lib import showarray, cluster, connected


class ProcessedImage:
    def __init__(self, engine, name, ext="jpg", batch=False):
        self.engine = engine
        self.config = engine.config
        C = self.config
        self.name = name
        self.ext = ext
        self.empty = True
        self.batch = batch
        self.stages = {}

        path = f"{C.PREOCR_INPUT}/{name}.{ext}"
        if not batch and not os.path.exists(path):
            sys.stderr.write(f"Image file not found: {path}")
            return

        self.empty = False
        orig = cv2.imread(path)
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        self.stages = {"orig": orig, "gray": gray}

    def show(self, stage=None, **kwargs):
        """Displays a stage of an image.

        If no stage is passed, all stages are shown as thumbnails.
        """

        C = self.config

        stages = self.stages
        if stage is None:
            for s in C.STAGE_ORDER:
                if s not in stages:
                    continue
                img = stages[s]
                display(HTML(f"<div>{s}</div>"))
                showarray(img, width=400)
            return

        if stage not in stages:
            sys.stderr.write(f"Unknown stage: {stage}, showing original stage\n")
            stage = "orig"
        what = stages.get(stage, None)
        if what is None:
            sys.stderr.write(f"No stage: orig\n")
        else:
            showarray(what, **kwargs)

    def layer(self, stage):
        """Returns a stage of an image.
        """

        stages = self.stages

        if stage not in stages:
            sys.stderr.write(f"Unknown stage: {stage}, showing original stage\n")
            stage = "orig"
        what = stages.get(stage, None)
        if what is None:
            sys.stderr.write(f"No stage: orig\n")
        return what

    def write(self, name=None, ext=None, stage=None):
        """Writes a stage of an image to disk.

        If no stage is passed, all stages are printed.
        """

        C = self.config

        stages = self.stages
        if stage is None:
            for s in C.STAGE_ORDER:
                if s not in stages:
                    continue
                img = stages[s]
                path = f"{C.OCR_INPUT}/{name}-{s}.{ext}"
                cv2.imwrite(path, img)
            return

        if stage not in stages:
            sys.stderr.write(f"Unknown stage: {stage}, writing clean stage\n")
        what = stages.get(stage, "clean")
        if what is None:
            sys.stderr.write(f"No stage: clean\n")

        if name is None:
            name = self.name
        if ext is None:
            ext = self.ext
        path = f"{C.OCR_INPUT}/{name}-{stage}.{ext}"
        cv2.imwrite(path, what)

    def normalize(self):
        """Normalizes an image.

        It removes a stage that is unskewed: *rotated* and blurred.
        The same rotation will be applied to the original image,
        resulting in stage *normalized*.

        Unskewing is needed otherwise the footnote line will not be found.
        """

        if self.empty:
            return

        stages = self.stages
        orig = stages["orig"]
        gray = stages["gray"]

        blurred = cv2.GaussianBlur(gray, (21, 21), 60, 0)

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
        normalized = cv2.warpAffine(gray, M, (gray.shape[1], gray.shape[0]))
        normalizedC = cv2.warpAffine(orig, M, (orig.shape[1], orig.shape[0]))

        stages["rotated"] = rotated
        stages["normalized"] = normalized
        stages["normalizedC"] = normalizedC

    def histogram(self):
        """Add histograms to an image.

        A new stage of the image, *histogram*, is added.

        The histograms contain an indication of the amount of ink in
        horizontal and in vertical rows.

        The histogram values are preserved as well.
        """

        if self.empty:
            return

        stages = self.stages
        normalizedC = stages["normalizedC"]
        rotated = stages["rotated"]
        histogram = normalizedC.copy()

        self.histY = cv2.reduce(rotated, 1, cv2.REDUCE_AVG).reshape(-1)
        self.histX = cv2.reduce(rotated, 0, cv2.REDUCE_AVG).reshape(-1)
        for (hist, vert) in ((self.histY, True), (self.histX, False)):
            for (i, val) in enumerate(self.histY):
                color = (int(val), int(2 * val), int(val))
                index = (0, i) if vert else (i, 0)
                value = (val, i) if vert else (i, val)
                cv2.line(histogram, index, value, color, 1)
        stages["histogram"] = histogram

    def margins(self, upperLeeway=None, lowerLeeway=None):
        """Chop off margins of an image.

        A new stage of the image, *demargined*, is added.

        !!! caution "it is assumed that the image has a histogram"
            This method uses the histogram info of the image.
        """

        if self.empty:
            return

        C = self.config
        batch = self.batch

        threshold = C.MARGIN_THRESHOLD
        mcolor = C.MARGIN_COLOR
        gucolor = C.GRID_UPPER_COLOR
        glcolor = C.GRID_LOWER_COLOR
        engine = self.engine
        divisor = engine.divisor
        stages = self.stages
        normalized = stages["normalized"]
        normalizedC = stages["normalizedC"]
        demargined = normalized.copy()
        demarginedC = normalizedC.copy()

        histX = self.histX
        histY = self.histY

        if upperLeeway is None:
            upperLeeway = C.GRID_UPPER_LEEWAY
        if lowerLeeway is None:
            lowerLeeway = C.GRID_LOWER_LEEWAY

        (h, w) = normalized.shape[:2]
        for pixel in range(0, w):
            if histX[pixel] < threshold:
                cv2.line(demargined, (pixel, 0), (pixel, h), mcolor, 1)
                cv2.line(demarginedC, (pixel, 0), (pixel, h), mcolor, 1)

        uppers = [
            y
            for y in range(h - 1)
            if histY[y] <= threshold and histY[y + 1] > threshold
        ]
        lowers = [
            y
            for y in range(h - 1)
            if histY[y] > threshold and histY[y + 1] <= threshold
        ]
        inter = []

        cv2.rectangle(demargined, (0, 0), (w, uppers[0]), mcolor, -1)
        cv2.rectangle(demarginedC, (0, 0), (w, uppers[0]), mcolor, -1)
        (divh, divw) = divisor.shape[:2]

        divisorFound = (False, None)

        for (i, (upper, lower)) in enumerate(zip(uppers, lowers)):
            if i > 0:
                inter[i - 1][1] = upper
            inter.append([lower, None])
            roi = normalized[upper - 5 : lower + 4, 10 : w - 10]
            (roih, roiw) = roi.shape[:2]
            if roih < divh or roiw < divw:
                # divisor template exceeds roi image
                continue
            result = cv2.matchTemplate(roi, divisor, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.5)
            if loc[0].size:
                divisorFound = (True, roi)
                cv2.rectangle(demargined, (0, uppers[i]), (w, h), mcolor, -1)
                cv2.rectangle(demarginedC, (0, uppers[i]), (w, h), mcolor, -1)
                break
            else:
                continue
        inter.pop()

        if not batch:
            if divisorFound[0]:
                showarray(divisorFound[1])
            else:
                sys.stdout.write("no divisor on page\n")

        for (upper, lower) in inter:
            cv2.line(
                demarginedC,
                (10, upper - upperLeeway),
                (w - 10, upper - upperLeeway),
                gucolor,
                2,
            )
            cv2.line(
                demarginedC,
                (10, lower + lowerLeeway),
                (w - 10, lower + lowerLeeway),
                glcolor,
                2,
            )
            cv2.line(
                demarginedC,
                (10, upper - upperLeeway),
                (10, lower + lowerLeeway),
                gucolor,
                2,
            )
            cv2.line(
                demarginedC,
                (w - 10, upper - upperLeeway),
                (w - 10, lower + lowerLeeway),
                gucolor,
                2,
            )

        self.stages["demargined"] = demargined
        self.stages["demarginedC"] = demarginedC

    def clean(self, element=None, bw=None, acc=None, threshold=None, ratio=None):
        """Remove marks from the image.

        The image is cleaned of a given list of elements.

        New stages of the image are added:

        *   *clean* all targeted marks removed
        *   *cleanh* all targeted marks highlighted in light gray
        *   *boxed* all targeted marks boxed in light gray
        """

        if self.empty:
            return

        C = self.config
        engine = self.engine
        batch = self.batch

        (hlclr, hlclrc, hlbrd) = C.CLEAN_HIGHLIGHT

        if threshold is None:
            threshold = C.CLEAN_CONNECT_THRESHOLD
        if ratio is None:
            ratio = C.CLEAN_CONNECT_RATIO

        if not batch:
            if bw is None:
                bw = C.BORDER_WIDTH
            if bw <= 0:
                sys.stderr.write(f"border width in clean: changed {bw} to 1\n")
                bw = 1
            if acc is None:
                acc = C.ACCURACY
            if element is None:
                for elemName in C.ELEMENT_INSTRUCTIONS:
                    engine.loadElement(elemName, acc, bw)
                searchElements = set(C.ELEMENT_INSTRUCTIONS)
            elif type(element) in {list, tuple}:
                searchElements = set()
                for el in element:
                    engine.loadElement(el, acc, bw)
                    searchElements.add(el)
            else:
                engine.loadElement(element, acc, bw)
                searchElements = {element}

        color = C.CLEAN_COLOR

        stages = self.stages
        demargined = stages.get("demargined", stages["gray"])
        demarginedC = stages.get("demarginedC", stages["orig"])
        resultStages = ("clean",) if batch else ("clean", "cleanh", "boxed")
        for stage in resultStages:
            stages[stage] = (demarginedC if stage == "boxed" else demargined).copy()

        tasks = [
            (stage, stages[stage], color[stage], bw if stage == "boxed" else -1)
            for stage in resultStages
        ]

        info = {}
        maxHits = C.CLEAN_MAX_HITS

        for elemName in engine.elements if batch else searchElements:
            elemInfo = engine.elements[elemName]
            elem = elemInfo["image"]
            if batch:
                bw = elemInfo["bw"]
                acc = elemInfo["acc"]
            (h, w) = elem.shape[:2]
            result = cv2.matchTemplate(demargined, elem, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= acc)
            pts = list(zip(*loc))
            if len(pts) > maxHits:
                sys.stderr.write(
                    f"Too many hit points for template {elemName}:"
                    f" {len(pts)} > {maxHits}\n"
                    f"Increase accuracy for this template\n"
                )
                continue
            if not pts:
                if not batch:
                    sys.stderr.write(f'No hit points for template "{elemName}"\n')
                continue
            clusters = cluster(pts, result)
            if not batch:
                info[elemName] = {}
                einfo = info[elemName]
                einfo["npoints"] = len(pts)
                einfo["hits"] = []
                einfo["connected"] = 0
                einfo["border"] = bw
                einfo["ratio"] = ratio
                hits = einfo["hits"]
            else:
                hits = []

            for (pt, bestValue) in clusters:
                connDegree = connected(h, w, bw, threshold, demargined, pt)
                if not batch:
                    hits.append(dict(accuracy=bestValue, conn=connDegree, point=pt))
                hit = (
                    (pt[1], pt[0]),
                    (pt[1] + w, pt[0] + h),
                )
                for (stage, im, clr, brd) in tasks:
                    isBoxed = stage == "boxed"
                    if connDegree > ratio:
                        if isBoxed:
                            cv2.rectangle(im, *hit, hlclrc, hlbrd)
                    else:
                        theClr = hlclr if isBoxed else clr
                        theBrd = hlbrd if isBoxed else -1
                        cv2.rectangle(im, *hit, theClr, theBrd)

        self.cleanInfo = info

    def showCleanInfo(self):
        engine = self.engine
        info = self.cleanInfo
        total = 0

        for elemName in sorted(info):
            einfo = info[elemName]
            bw = einfo["border"]
            ratio = einfo["ratio"]
            showarray(engine.elements[elemName]["image"])
            totalHits = len(einfo["hits"])
            connHits = len([h for h in einfo["hits"] if h["conn"] > ratio])
            realHits = totalHits - connHits
            total += realHits
            print(
                f"{elemName:<12} with border {bw}:\n"
                f" {realHits} hits in {einfo['npoints']} points\n"
                f" {connHits} connected hits removed from {totalHits} candidate hits"
            )
            for hit in einfo["hits"]:
                conn = hit["conn"]
                ast = "*" if conn > ratio else " "
                print(
                    f"\t{ast}hit"
                    f" with accuracy {hit['accuracy']:5.2f}"
                    f" with connectivity {ast}{hit['conn']:5.2f}"
                    f" reached by {hit['point']}"
                )

        print(f"{total} marks wiped clean")
