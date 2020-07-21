import os
import io
import collections
from itertools import chain, groupby
from tempfile import NamedTemporaryFile

import numpy as np
import PIL.Image
from IPython.display import HTML, Image, display
import cv2

from tf.core.helpers import rangesFromList, rangesFromSet, specFromRanges

EXTENSIONS = set(
    """
    jpeg
    jpg
    png
    tif
    tiff
""".strip().split()
)

MARK_HEADERS = """
    band
    seq
    mark
    kept
    value
    connectdegree
    connectborder
    top
    bottom
    left
    right
""".strip().split()

FONT = cv2.FONT_HERSHEY_SIMPLEX


def tempFile():
    """Get a temporary file.
    """

    return NamedTemporaryFile(mode="w", dir=".")


def img(data):
    """Produce an image with its data packaged into a HTML <img> element.
    """

    return f"""<img src="data:image/jpeg;base64,{data}">"""


def showImage(a, fmt="jpeg", **kwargs):
    """Show one or more images.
    """

    if type(a) in {list, tuple}:
        ads = []
        for ae in a:
            ai = np.uint8(np.clip(ae, 0, 255))
            f = io.BytesIO()
            PIL.Image.fromarray(ae).save(f, fmt)
            ad = Image(data=f.getvalue(), **kwargs)._repr_jpeg_()
            ads.append(ad)
        display(HTML(f"<div>{''.join(img(ad) for ad in ads)}</div>"))
    else:
        ai = np.uint8(np.clip(a, 0, 255))
        f = io.BytesIO()
        PIL.Image.fromarray(ai).save(f, fmt)
        display(Image(data=f.getvalue(), **kwargs))


def overlay(img, left, top, right, bottom, srcColor, dstColor):
    if right > left and bottom > top:
        roi = img[top:bottom, left:right]
        roi[np.where((roi == list(srcColor)).all(axis=2))] = dstColor


def splitext(f, withDot=True):
    (bare, ext) = os.path.splitext(f)
    if ext and not withDot:
        ext = ext[1:]
    return (bare, ext)


def imageFileList(imDir):
    if not os.path.exists(imDir):
        return []

    imageFiles = []
    with os.scandir(imDir) as it:
        for entry in it:
            name = entry.name
            (bare, ext) = splitext(name, withDot=False)

            if not name.startswith(".") and entry.is_file() and ext in EXTENSIONS:
                imageFiles.append(name)
    return sorted(imageFiles)


def imageFileListSub(imDir):
    if not os.path.exists(imDir):
        return {}
    imageFiles = {}
    with os.scandir(imDir) as it:
        for entry in it:
            name = entry.name
            if not name.startswith(".") and entry.is_dir():
                imageFiles[name] = imageFileList(f"{imDir}/{name}")
    return imageFiles


def pagesRep(source, asList=False):
    pages = [int(splitext(f)[0].lstrip("0")) for f in source]
    return pages if asList else specFromRanges(rangesFromList(pages))


def select(source, selection):
    if selection is None:
        return sorted(source)

    index = {int(splitext(f)[0].lstrip("0")): f for f in source}
    universe = set(index)
    if type(selection) is int:
        return sorted(index[n] for n in {selection} & universe)

    minu = min(universe, default=0)
    maxu = max(universe, default=0)
    selected = set()
    for rng in selection.split(","):
        parts = rng.split("-")
        if len(parts) == 2:
            (lower, upper) = parts
            lower = minu if lower == "" else int(lower)
            upper = maxu if upper == "" else int(upper)
        else:
            lower = int(parts[0])
            upper = lower
        selected |= set(range(lower, upper + 1)) & universe
    return sorted(index[n] for n in selected)


def cluster(points, result):
    def d(p1, p2):
        if p1 == p2:
            return 0
        (x1, y1) = p1
        (x2, y2) = p2
        return abs(x1 - x2) + abs(y1 - y2)

    clusters = []
    for (i, p) in enumerate(points):
        stored = False
        rp = result[p]
        for c in clusters:
            (q, rq) = c
            if d(p, q) <= 8:
                if rp > rq:
                    c[0] = p
                    c[1] = rp
                stored = True
                break
        if not stored:
            clusters.append([p, rp])
    return clusters


def measure(borderInside, borderOutside, threshold):
    connections = borderInside * borderOutside
    return np.where(connections > threshold)[0].size / borderOutside.size


def showit(label, texto, texti, val):
    print(f"{label}: = {val}")
    print("Outer", " ".join(f"{e:>3}" for e in texto))
    print("Inner", " ".join(f"{e:>3}" for e in texti))


def connected(markH, markW, bw, threshold, img, hitPoint, sides=None):
    """Determine how much ink borders on a given rectangle.

    Parameters
    ----------
    markH: integer
        height of the rectangle
    markW: integer
        width of the rectangle
    bw: integer
        width of the border around the rectangle that will be used to detect connections
    threshold:
        the value above which a connection is detected
    img: np array
        the source image
    hitPoint: (int, int)
        Y and X coordinate of top left corner of the rectangle in the image
    sides: string, optional `None`
        If `None`, computes connections on all sides.
        Otherwise it should be a string consisting of at most these characters:
        `l` (left), `r` (right), `t` (top), `b` (bottom).
        Only these sides will be computed.
    """

    (textH, textW) = img.shape
    (hitY, hitX) = hitPoint

    connDegree = 0
    nparts = 0

    realBw = min((bw, markW, markH))

    # left boundary

    fo = max((0, hitX - realBw)) if hitX > 0 else None
    if fo is not None and (sides is None or "l" in sides):
        to = hitX
        texto = np.array(
            (255 - img[hitY : hitY + markH, fo:to]).max(axis=1), dtype=np.uint16
        )
        fi = hitX
        ti = hitX + realBw
        texti = np.array(
            (255 - img[hitY : hitY + markH, fi:ti]).max(axis=1), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        connDegree += val
        nparts += 1

    # right boundary

    to = (
        min((textW, hitX + markW + realBw + 1))
        if hitX + markW + realBw < textW
        else None
    )
    if to is not None and (sides is None or "r" in sides):
        fo = hitX + markW
        texto = np.array(
            (255 - img[hitY : hitY + markH, fo:to]).max(axis=1), dtype=np.uint16
        )
        fi = hitX + markW - realBw
        ti = hitX + markW
        texti = np.array(
            (255 - img[hitY : hitY + markH, fi:ti]).max(axis=1), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        connDegree += val
        nparts += 1

    # top boundary

    f = max((0, hitY - realBw)) if hitY > 0 else None
    if f is not None and (sides is None or "t" in sides):
        t = hitY
        texto = np.array(
            (255 - img[f:t, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
        )
        fi = hitY
        ti = hitY + realBw + 1
        texti = np.array(
            (255 - img[fi:ti, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        connDegree += val
        nparts += 1

    # bottom boundary

    t = (
        min((textH - 1, hitY + markH + realBw + 1))
        if hitY + markH + realBw < textH
        else None
    )
    if t is not None and (sides is None or "b" in sides):
        f = hitY + markH
        texto = np.array(
            (255 - img[f:t, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
        )
        ti = hitY + markH
        fi = hitY + markH - realBw
        texti = np.array(
            (255 - img[fi:ti, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        connDegree += val
        nparts += 1

    return connDegree


def removeSkewStripes(img, skewBorder, skewColor):
    (imH, imW) = img.shape[0:2]
    if min((imH, imW)) < skewBorder * 10:
        return
    for rect in (
        ((0, 0), (skewBorder, imH)),
        ((0, 0), (imW, skewBorder)),
        ((imW, imH), (imW - skewBorder, 0)),
        ((imW, imH), (0, imH - skewBorder)),
    ):
        cv2.rectangle(img, *rect, skewColor, -1)


def addBox(C, im, top, bottom, left, right, kept, band, seq, connDegree):
    fill = C.boxRemainRGB if kept else C.boxDeleteRGB
    fillN = C.boxRemainNRGB if kept else C.boxDeleteNRGB
    border = C.boxBorder

    cv2.rectangle(im, (left, top), (right, bottom), fill, border)
    addSeq(
        im, top, bottom, left, right, border, fillN, band, seq, connDegree,
    )


def addSeq(
    img,
    top,
    bottom,
    left,
    right,
    frameWidth,
    frameColor,
    band,
    markSeq,
    connectionDegree,
    size=0.5,
    weight=1,
):
    colorDeg = (100, 100, 255)
    ptSeq = (left, top - frameWidth - 2)
    ptDeg = (left, bottom + frameWidth + 8)
    cv2.putText(
        img,
        f"{'' if band == 'main' else band[0]}{markSeq}",
        ptSeq,
        FONT,
        size,
        frameColor,
        weight,
        cv2.LINE_AA,
    )
    connectionDegree = int(round(connectionDegree * 100))
    if connectionDegree:
        cv2.putText(
            img,
            str(connectionDegree),
            ptDeg,
            FONT,
            size,
            colorDeg,
            weight,
            cv2.LINE_AA,
        )


def addStripe(img, top, left, right, marginX, letterColor, stripe, kind, size=1.0):
    weight = 3
    offsetX = 80 + marginX
    halfOffsetX = offsetX // 2
    offsetY = 60

    x = halfOffsetX if kind == "l" or kind == "" else (right - offsetX)
    y = top + offsetY
    sep = "" if not kind else "-"
    cv2.putText(
        img,
        f"{stripe}{sep}{kind}",
        (x, y),
        FONT,
        size,
        letterColor,
        weight,
        cv2.LINE_AA,
    )


def addHStroke(
    img, isTop, i, column, thickness, top, left, right, letterColor, size=1.0
):
    weight = 3
    colRep = f"-{column}" if column else ""
    text = f"{'T' if isTop else 'B'}{i}{colRep}"
    offsetX = 60
    offsetY = 30 if isTop else -30 - 2 * thickness
    x = left + (right - left - offsetX) // 2
    y = top - offsetY

    cv2.putText(
        img, text, (x, y), FONT, size, letterColor, weight, cv2.LINE_AA,
    )


def storeCleanInfo(source):
    data = []
    data.append(MARK_HEADERS)

    for (band, markInfo) in sorted(source.items()):
        for ((seq, mark), entries) in sorted(markInfo.items()):
            for entry in sorted(entries):
                data.append((band, seq, mark, *entry))
    return data


def loadCleanInfo(self, data):
    cInfo = {}

    for (band, seq, mark, *entry) in data:
        cInfo.setdefault(band, {}).setdefault((seq, mark), []).append(entry)

    return cInfo


def getMargins(hist, width, threshold):
    """Get margins from a histogram.

    The margins of a histogram are the coordinates where the histogram reaches a
    threshold for the first time and for the last time.

    We deliver the pairs (0, xFirst) and (xLast, maxWidth) if there are points
    above the threshold, and (0, maxW) otherwise.


    Parameters
    ----------
    hist: [int]
        Source array of pixel values
    width: int
        Maximum index of the source array
    threshold: int
        Value below which pixels count as zero
    """
    chunks = [
        [i for (i, value) in it]
        for (key, it) in groupby(enumerate(hist), key=lambda x: x[1] >= threshold)
        if key >= threshold
    ]
    w = len(hist)
    return ((0, chunks[0][0]), (chunks[-1][-1], w)) if chunks else ((0, w),)


def parseStages(stage, allStages, sortedStages, error):
    doStages = (
        allStages
        if stage is None
        else set()
        if not stage
        else set(stage.split(","))
        if type(stage) is str
        else set(stage)
    )
    illegalStages = doStages - allStages
    if illegalStages:
        error(f"Will skip illegal stages: {', '.join(sorted(illegalStages))}")

    doStages = doStages - illegalStages

    return tuple(s for s in sortedStages if s in doStages)


def parseBands(band, allBands, error):
    sortedBands = sorted(allBands)
    doBands = (
        allBands
        if band is None
        else set(band.split(","))
        if type(band) is str
        else set(band)
    )
    illegalBands = doBands - allBands
    if illegalBands:
        error(f"Will skip illegal bands: {', '.join(sorted(illegalBands))}")

    doBands -= illegalBands
    return tuple(b for b in sortedBands if b in doBands)


def parseMarks(mark, allMarks, bands, error):
    markIndex = {}
    for (band, bandMarks) in allMarks.items():
        for m in bandMarks:
            markIndex.setdefault(m, set()).add(band)

    doMarks = (
        set()
        if mark is None
        else set(chain.from_iterable(allMarks.get(band, ()) for band in bands))
        if mark == ""
        else set(mark.split(","))
        if type(mark) is str
        else set(mark)
    )
    illegalMarks = doMarks - set(markIndex)
    if illegalMarks:
        error(f"Will skip illegal marks: {', '.join(sorted(illegalMarks))}")

    doMarks -= illegalMarks
    return doMarks


def findRuns(x):
    """Find runs of consecutive items in an array.

    Credits:
    [Alistair Miles](https://gist.github.com/alimanfoo/c5977e87111abe8127453b21204c1065)
    """

    # ensure array
    x = np.asanyarray(x)
    if x.ndim != 1:
        raise ValueError("only 1D array supported")
    n = x.shape[0]

    # handle empty array
    if n == 0:
        return np.array([]), np.array([]), np.array([])

    else:
        # find run starts
        loc_run_start = np.empty(n, dtype=bool)
        loc_run_start[0] = True
        np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
        run_starts = np.nonzero(loc_run_start)[0]

        # find run values
        run_values = x[loc_run_start]

        # find run lengths
        run_lengths = np.diff(np.append(run_starts, n))

        return run_values, run_starts, run_lengths


def getStretches(C, info, stages, horizontal):
    """Gets significant horizontal or vertical strokes.

    Significant strokes are those that are not part of letters,
    but ones that are used as separators, e.g. of footnotes and columns.

    We single out 1-pixel wide lines longer than a small threshold
    in the appropriate direction, and blacken the rest.
    Then we blur in the perpendicular direction.
    Now we single out longer 1-pixel wide lines and cluster in the perpendicular
    direction.

    Clusters are line segments with nearly the same constant coordinate.
    If we do horizontal lines, clusters are pairs of x coordinates
    for one y coordinate.
    If we do vertical lines, clusters are pairs of y coordinates
    for one x coordinate.
    We return the clusters, i.e. a dict keyed by the fixed coordinate and
    valued by the pair of segment coordinates.


    Parameters
    ----------
    C: object
        The configuration object of the book engine.
    info: function
        To print messages to the console
    stages: dict
        Intermediate cv2 images, keyed by stage name
    horizontal: boolean
        Whether we do horizontal of vertical lines.

    Returns
    -------
    dict
        Per fixed coordinate the list of line segments on that coordinate.
        A line segment is specified by its begin and end values and the thickness of
        the cluster it is in.
    """

    debug = C.debug
    strokeColor = C.horizontalStrokeRGB if horizontal else C.verticalStrokeRGB

    normalized = stages["normalized"]
    layout = stages["layout"]
    img = normalized if horizontal else normalized.T
    out = layout if horizontal else cv2.transpose(layout)
    label = "HOR" if horizontal else "VER"

    (maxH, maxW) = img.shape[0:2]

    minLength = maxW // 30 if horizontal else maxH // 50
    afterLength = maxW // 10 if horizontal else maxH // 17

    # initial blur

    initBlur = (13, 7) if horizontal else (7, 13)

    blurred = cv2.GaussianBlur(img, initBlur, 0, 0)
    (th, threshed) = cv2.threshold(
        blurred, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )

    # collect lines of a minimal length

    sliced = threshed.copy()
    for (n, row) in enumerate(sliced):
        for (val, start, length) in zip(*findRuns(row)):
            if val == 255:
                if length < minLength:
                    row[start : start + length] = 0

    if debug > 1:
        showImage(sliced if horizontal else sliced.T)

    # second blur, now stronger

    strongBlur = (21, 11) if horizontal else (11, 21)

    blurred = cv2.GaussianBlur(sliced, strongBlur, 0, 0)
    (th, threshed) = cv2.threshold(
        blurred, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )

    if debug > 1:
        showImage(threshed if horizontal else threshed.T)

    # collect lines of a certain length, longer than before

    lines = collections.defaultdict(set)
    for (n, row) in enumerate(threshed):
        for (val, start, length) in zip(*findRuns(row)):
            if val == 255:
                if length >= afterLength:
                    lines[n] |= set(range(start, start + length))

    # cluster lines in bins corresponding to their constant coordinates:
    # horizontal lines are clustered in bins on their y coordinate.
    # vertical lines are clustered in bins on their x coordinate.

    bins = []
    for n in sorted(lines):
        found = False
        for (i, (b, e)) in enumerate(bins):
            if b - 3 <= n <= e + 3:
                if n < b:
                    bins[i][0] = n
                if n > e:
                    bins[i][1] = n
                found = True
                break
        if not found:
            bins.append([n, n])

    # combine the segments of all lines that are in the same bin

    stretches = {}
    for (b, e) in bins:
        middle = (b + e) // 2
        thickness = (abs(e - b) + 1) // 2
        if thickness <= 1:
            continue
        theseStretches = set()
        for n in range(b, e):
            if n in lines:
                theseStretches |= lines[n]
        segments = []
        for (m1, m2) in rangesFromSet(theseStretches):
            segments.append((m1, m2 + 1, thickness))
        stretches[middle] = segments

    for (n, segments) in sorted(stretches.items()):
        for (f, t, half) in segments:
            info(f"{label} @ {n:>4} thick={half:>2} from {f:>4} to {t:>4}", tm=False)
            cv2.rectangle(out, (f, n - half - 2), (t, n + half + 2), strokeColor, 3)

    stages["layout"] = out if horizontal else cv2.transpose(out)

    if debug > 0:
        showImage(stages["layout"])
    return stretches


def getBandsFromHist(C, height, histY):
    # invariant:
    # not inline => not dip
    # #uppers == #lowers      if (inline and dip) or (not inline)
    # #uppers == #lowers + 1  if (inline and not dip)

    threshold = C.marginThresholdY
    threshold2 = C.marginThreshold2Y

    dip = False
    inline = False
    uppers = []
    lowers = []

    for y in range(height):
        hist = histY[y]
        if inline:
            if hist >= threshold2:
                if dip:
                    lowers[-1] = y
            elif hist <= threshold:
                if not dip:
                    lowers.append(y)
                inline = False
                dip = False
            else:
                if dip:
                    lowers[-1] = y
                else:
                    lowers.append(y)
                    dip = True
        else:
            if hist >= threshold2:
                uppers.append(y)
                inline = True
                dip = False

    # guarantee that len(uppers) == len(lowers) in case they are different
    # by invariant: that only happens if inline and not dip

    if inline and not dip:
        lowers.append(y)

    return (uppers, lowers)


def applyBandOffset(C, height, kind, uppers, lowers, inter=False):
    offsetBand = C.offsetBand

    (top, bottom) = offsetBand[kind]

    def offset(x, off):
        x += off
        return 0 if x < 0 else height if x > height else x

    return (
        tuple(offset(x, top) for x in (lowers[:-1] if inter else uppers)),
        tuple(offset(x, bottom) for x in (uppers[1:] if inter else lowers)),
    )


def adjustVertical(C, rotated, left, right, yMin, yMinLee, yMax, yMaxLee, preferExtend):
    roiIn = rotated[yMinLee:yMaxLee, left:right]
    histY = cv2.reduce(roiIn, 1, cv2.REDUCE_AVG).reshape(-1)
    theYMin = None
    theYMax = None

    if yMin == yMinLee:
        theYMin = yMin
    if yMax == yMaxLee:
        theYMax = yMax
    if theYMin is not None and theYMax is not None:
        return (theYMin, theYMax)

    normH = yMax - yMin
    normHLee = yMaxLee - yMinLee

    (uppers, lowers) = applyBandOffset(
        C, normHLee, "broad", *getBandsFromHist(C, normHLee, histY)
    )

    topLee = yMin - yMinLee
    botLee = topLee + normH

    if theYMin is None:
        if preferExtend:
            # look for the first lower boundary in the top of the strict region
            # then take the corresponding upper boundary
            for (i, lower) in enumerate(lowers):
                if lower >= topLee:
                    theYMin = uppers[i]
                    break
        else:
            # look for the first upper boundary in the top of the strict region
            for upper in uppers:
                if upper > topLee:
                    theYMin = upper
                    break
        theYMin = yMin if theYMin is None else yMinLee + theYMin

    if theYMax is None:
        if preferExtend:
            # look for the last upper boundary in the bottom of the strict region
            # then take the corresponding lower boundary
            for (i, upper) in enumerate(reversed(uppers)):
                if upper <= botLee:
                    theYMax = lowers[-i - 1]
                    break
        else:
            # look for the last lower boundary in the bottom of the strict region
            for lower in reversed(lowers):
                if lower < botLee:
                    theYMax = lower
                    break
        theYMax = yMax if theYMax is None else yMinLee + theYMax

    return (theYMin, theYMax)
