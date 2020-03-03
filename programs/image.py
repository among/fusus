import sys
import io
import cv2
import numpy as np
import PIL.Image
from IPython.display import Image, display


COLOR = {
    None: (200, 200, 200),
    False: (255, 0, 255),
    True: (255, 255, 255),
}

BORDER = {
    False: 3,
    True: -1,
}


def showarray(a, fmt="jpeg", **kwargs):
    a = np.uint8(np.clip(a, 0, 255))
    f = io.BytesIO()
    PIL.Image.fromarray(a).save(f, fmt)
    display(Image(data=f.getvalue(), **kwargs))


class ProcessedImage:
    def __init__(self, folder, name, ext="jpg"):
        self.folder = folder
        self.name = name
        self.ext = ext
        path = f"{folder}/{name}.{ext}"
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.stages = {None: img, "gray": gray}

    def show(self, stage=None, **kwargs):
        stages = self.stages
        if stage not in stages:
            sys.stderr.write(f"Unknown stage: {stage}, showing original stage")
        what = stages.get(stage, None)
        showarray(what, **kwargs)

    def write(self, folder=None, name=None, ext=None, stage=None):
        stages = self.stages
        if stage not in stages:
            sys.stderr.write(f"Unknown stage: {stage}, writing original stage")
        what = stages.get(stage, None)
        whatRep = "" if what is None else f"-{stage}"

        if folder is None:
            folder = self.folder
        if name is None:
            name = self.name
        if ext is None:
            ext = self.ext
        path = f"{folder}/{name}{whatRep}.{ext}"
        cv2.imwrite(path, what)

    def normalize(self):
        """Normalizes an image.

        It removes a stage that is unskewed: *rotated* and blurred.
        The same rotation will be applied to the original image,
        resulting in stage *normalized*.

        Unskewing is needed otherwise the footnote line will not be found.
        """

        stages = self.stages
        img = stages[None]
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

        # rotated = threshed
        # normalized = gray
        # normalizedC = img

        rotated = cv2.warpAffine(threshed, M, (threshed.shape[1], threshed.shape[0]))
        normalized = cv2.warpAffine(gray, M, (gray.shape[1], gray.shape[0]))
        normalizedC = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

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

    def margins(self, divisor):
        """Chop off margins of an image.

        A new stage of the image, *demargined*, is added.

        !!! caution "it is assumed that the image has a histogram"
            This method uses the histogram info of the image.
        """

        THRESHOLD = 5
        MARGIN_COLOR = (240, 240, 240)

        stages = self.stages
        normalized = stages["normalized"]
        normalizedC = stages["normalizedC"]
        demargined = normalized.copy()
        demarginedC = normalizedC.copy()

        histX = self.histX
        histY = self.histY

        (H, W) = normalized.shape[:2]
        for pixel in range(0, W):
            if histX[pixel] < THRESHOLD:
                cv2.line(demargined, (pixel, 0), (pixel, H), MARGIN_COLOR, 1)
                cv2.line(demarginedC, (pixel, 0), (pixel, H), MARGIN_COLOR, 1)

        uppers = [
            y
            for y in range(H - 1)
            if histY[y] <= THRESHOLD and histY[y + 1] > THRESHOLD
        ]
        lowers = [
            y
            for y in range(H - 1)
            if histY[y] > THRESHOLD and histY[y + 1] <= THRESHOLD
        ]

        cv2.rectangle(demargined, (0, 0), (W, uppers[0]), MARGIN_COLOR, -1)
        cv2.rectangle(demarginedC, (0, 0), (W, uppers[0]), MARGIN_COLOR, -1)

        for i in range(1, len(uppers)):
            roi = normalized[uppers[i] - 5 : lowers[i] + 4, 10 : W - 10]
            result = cv2.matchTemplate(roi, divisor, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.5)
            if loc[0].size:
                cv2.rectangle(demargined, (0, uppers[i]), (W, H), MARGIN_COLOR, -1)
                cv2.rectangle(demarginedC, (0, uppers[i]), (W, H), MARGIN_COLOR, -1)
                break
            else:
                continue

        self.stages["demargined"] = demargined
        self.stages["demarginedC"] = demarginedC

    def clean(self, elements, destroy):
        """Remove marks from the image.

        The image is cleaned of a given list of elements.

        A new stage of the image, *clean*, is added.
        """

        color = COLOR[destroy]
        colorG = COLOR[True] if destroy else COLOR[None]
        border = BORDER[destroy]

        stages = self.stages
        demargined = stages["demargined"]
        demarginedC = stages["demarginedC"]
        clean = demargined.copy()
        cleanC = demarginedC.copy()

        for (elem, acc) in elements:
            (H, W) = elem.shape[:2]
            result = cv2.matchTemplate(demargined, elem, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= acc)
            for pt in zip(*loc[::-1]):
                cv2.rectangle(clean, pt, (pt[0] + W, pt[1] + H), colorG, border)
                cv2.rectangle(cleanC, pt, (pt[0] + W, pt[1] + H), color, border)

        stages["clean"] = clean
        stages["cleanC"] = cleanC
