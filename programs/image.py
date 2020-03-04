import sys
import io
import cv2
import numpy as np
import PIL.Image
from IPython.display import HTML, Image, display


def showarray(a, fmt="jpeg", **kwargs):
    a = np.uint8(np.clip(a, 0, 255))
    f = io.BytesIO()
    PIL.Image.fromarray(a).save(f, fmt)
    display(Image(data=f.getvalue(), **kwargs))


def cluster(points):
    def d(p1, p2):
        if p1 == p2:
            return 0
        (x1, y1) = p1
        (x2, y2) = p2
        return abs(x1 - x2) + abs(y1 - y2)

    clusters = []
    for p in points:
        stored = False
        for c in clusters:
            for q in c:
                if d(p, q) <= 2:
                    c.append(p)
                    stored = True
                    break
            if stored:
                break
        if not stored:
            clusters.append([p])
    return clusters


class ProcessedImage:
    def __init__(self, engine, name, ext="jpg"):
        self.engine = engine
        self.config = engine.config
        C = self.config
        self.name = name
        self.ext = ext
        path = f"{C.PREOCR_INPUT}/{name}.{ext}"
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
            sys.stderr.write(f"Unknown stage: {stage}, showing original stage")
            stage = "orig"
        what = stages.get(stage, None)
        if what is None:
            sys.stderr.write(f"No stage: orig")
        else:
            showarray(what, **kwargs)

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
            sys.stderr.write(f"Unknown stage: {stage}, writing clean stage")
        what = stages.get(stage, "clean")
        if what is None:
            sys.stderr.write(f"No stage: clean")

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

    def margins(self):
        """Chop off margins of an image.

        A new stage of the image, *demargined*, is added.

        !!! caution "it is assumed that the image has a histogram"
            This method uses the histogram info of the image.
        """

        C = self.config

        threshold = C.MARGIN_THRESHOLD
        mcolor = C.MARGIN_COLOR
        engine = self.engine
        divisor = engine.divisor
        stages = self.stages
        normalized = stages["normalized"]
        normalizedC = stages["normalizedC"]
        demargined = normalized.copy()
        demarginedC = normalizedC.copy()

        histX = self.histX
        histY = self.histY

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

        cv2.rectangle(demargined, (0, 0), (w, uppers[0]), mcolor, -1)
        cv2.rectangle(demarginedC, (0, 0), (w, uppers[0]), mcolor, -1)

        for i in range(1, len(uppers)):
            roi = normalized[uppers[i] - 5 : lowers[i] + 4, 10 : w - 10]
            result = cv2.matchTemplate(roi, divisor, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.5)
            if loc[0].size:
                cv2.rectangle(demargined, (0, uppers[i]), (w, h), mcolor, -1)
                cv2.rectangle(demarginedC, (0, uppers[i]), (w, h), mcolor, -1)
                break
            else:
                continue

        self.stages["demargined"] = demargined
        self.stages["demarginedC"] = demarginedC

    def clean(self, element=None, bw=None, acc=None):
        """Remove marks from the image.

        The image is cleaned of a given list of elements.

        New stages of the image are added:

        *   *clean* all targeted marks removed
        *   *cleanh* all targeted marks highlighted in light gray
        *   *boxed* all targeted marks boxed in light gray
        """

        C = self.config
        engine = self.engine

        if bw is None:
            bw = C.BORDER_WIDTH

        if element is None:
            for elemName in C.ELEMENT_INSTRUCTIONS:
                engine.loadElement(elemName, bw)
            searchElements = (
                C.ELEMENT_INSTRUCTIONS
                if acc is None
                else {e: acc for e in C.ELEMENT_INSTRUCTIONS}
            )
        elif type(element) in {list, tuple}:
            searchElements = {}
            for el in element:
                engine.loadElement(el, bw)
                acc = C.ELEMENT_INSTRUCTIONS.get(el, C.ACCURACY) if acc is None else acc
                searchElements[el] = acc
        else:
            engine.loadElement(element, bw)
            acc = (
                C.ELEMENT_INSTRUCTIONS.get(element, C.ACCURACY) if acc is None else acc
            )
            searchElements = {element: acc}

        color = C.CLEAN_COLOR
        hbw = int(round(0.5 * bw))

        stages = self.stages
        demargined = stages.get("demargined", stages["gray"])
        demarginedC = stages.get("demarginedC", stages["orig"])
        resultStages = ("clean", "cleanh", "boxed")
        for stage in resultStages:
            stages[stage] = (demarginedC if stage == "boxed" else demargined).copy()

        tasks = [
            (stages[stage], color[stage], bw if stage == "boxed" else -1)
            for stage in resultStages
        ]

        info = {}
        for (elemName, acc) in searchElements.items():
            elem = engine.elements[elemName][bw]
            (h, w) = elem.shape[:2]
            result = cv2.matchTemplate(demargined, elem, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= acc)
            pts = list(zip(*loc))
            if not pts:
                continue
            clusters = cluster(pts)
            info[elemName] = {}
            einfo = info[elemName]
            einfo["npoints"] = len(pts)
            einfo["nclusters"] = len(clusters)
            einfo["hits"] = []
            einfo["border"] = bw
            hits = einfo["hits"]
            for cl in clusters:
                bestValue = max(result[p] for p in cl)
                bestPoints = [p for p in cl if result[p] == bestValue]
                pt = bestPoints[0]
                hits.append(
                    dict(
                        length=len(cl),
                        accuracy=bestValue,
                        nbestPoints=len(bestPoints),
                        point=pt,
                    )
                )
                hit = (
                    (pt[1] + hbw, pt[0] + hbw),
                    (pt[1] + w - hbw, pt[0] + h - hbw),
                )
                for (im, clr, brd) in tasks:
                    cv2.rectangle(im, *hit, clr, brd)

        self.cleanInfo = info

    def showCleanInfo(self):
        engine = self.engine
        info = self.cleanInfo
        total = 0

        for elemName in sorted(info):
            einfo = info[elemName]
            bw = einfo["border"]
            showarray(engine.elements[elemName][bw])
            print(
                f"{elemName:<12} with border {bw}:"
                f" {einfo['nclusters']} x in {einfo['npoints']} points"
            )
            for hit in einfo["hits"]:
                print(
                    f"\tcluster of size {hit['length']:>2}"
                    f" with accuracy {hit['accuracy']:5.2f}"
                    f" reached by {hit['nbestPoints']:>2} points"
                    f" - chosen {hit['point']}"
                )
                total += 1

        print(f"{total} marks wiped clean")
