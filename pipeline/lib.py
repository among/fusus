import os
import io
import collections
from itertools import chain, groupby
from tempfile import NamedTemporaryFile

import numpy as np
from scipy.signal import find_peaks

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
    """Colors a region of an image with care.

    A selected region of an image can be given a uniform color,
    where only pixels are changed that have an exact given color.

    In this way you can replace all the white with gray, for example,
    without wiping out existing non-white pixels.

    Parameters
    ----------
    img: np array
        The image to be overlain with a new color
    (left, top, right, bottom): (int, int, int, int)
        The region in the image to be colored
    srcColor: RGB color
        The color of the pixels that may be replaced.
    dstColor:
        The new color of the replaced pixels.
    """
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


def addBox(C, im, left, top, right, bottom, kept, band, seq, connDegree):
    fill = C.boxRemainRGB if kept else C.boxDeleteRGB
    fillN = C.boxRemainNRGB if kept else C.boxDeleteNRGB
    border = C.boxBorder

    cv2.rectangle(im, (left, top), (right, bottom), fill, border)
    addSeq(
        im, left, top, right, bottom, border, fillN, band, seq, connDegree,
    )


def addSeq(
    img,
    left,
    top,
    right,
    bottom,
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


def getStretches(C, info, stages, horizontal, batch):
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
    batch: boolean
        Whether we run in batch mode.

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
    img = normalized if horizontal else normalized.T
    label = "HOR" if horizontal else "VER"

    if not batch:
        layout = stages["layout"]
        out = layout if horizontal else cv2.transpose(layout)

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
            if not batch:
                cv2.rectangle(out, (f, n - half - 2), (t, n + half + 2), strokeColor, 3)

    if not batch:
        stages["layout"] = out if horizontal else cv2.transpose(out)

    if not batch and debug > 1:
        showImage(stages["layout"])
    return stretches


def getStripes(stages, stretchesV):
    """Infer horizontal stripes from a set of vertical bars.

    A vertical bar defines a stripe on the page, i.e. a horizontal band that
    contains that bar.

    Between the vertical bars there are also stripes, they are undivided stripes.

    We assume the vertical bars split the page in two portions, and not more,
    and that they occur more or less in the middle of the page.

    If many vertical bars have been detected, we sort them by y1 ascending and then
    y2 descending and then by x.

    We filter the bars: if the last bar reached to y = height, we only consider
    bars that start lower than height.

    !!! note "Fine tuning needed later on"
        The vertical strokes give a rough estimate:
        it is possible that they start and end in the middle of the lines beside them.
        We will need histograms for the fine tuning.

    Parameters
    ----------
    stages: dict
        We need access to the normalized stage to get the page size.
    stretchesV: dict
        Vertical line segments per x-coordinate, as delivered by `getStretches`.

    Returns
    -------
    list
        A list of stripes, specified as (x, y1, y2) values,
        where the y-coordinates y1 and y2 specify the vertical extent of the stripe,
        and x is the x coordinate of the dividing vertical stroke if there is one
        and `None` otherwise.
    """

    normalized = stages["normalized"]
    (maxH, maxW) = normalized.shape[0:2]
    lastHeight = 0
    segments = []
    for (x, ys) in stretchesV.items():
        for (y1, y2, thickness) in ys:
            segments.append((y1, y2, x, thickness))
    stripes = []
    for (y1, y2, x, thickness) in sorted(
        segments, key=lambda z: (z[0], -z[1], -z[3], -z[2] or -1)
    ):
        if y1 > lastHeight:
            stripes.append((None, lastHeight, y1))
            stripes.append((x, y1, y2))
            lastHeight = y2
    if lastHeight < maxH:
        stripes.append((None, lastHeight, maxH))
    return stripes


def getBlocks(C, stages, stripes, batch):
    """Fine-tune stripes into blocks.

    We enlarge the stripes vertically by roughly a line height
    and call `adjustVertical` to get precise vertical demarcations
    for the blocks at both sides of the stripe if there is one or else
    for the undivided stripe.

    The idea is:

    If a stripe has a vertical bar, we slightly extend the boxes left and right
    so that the top and bottom lines next to the bar are completely included.

    If a stripe has no vertical bar, we shrink the box
    so that partial top and bottom lines are delegated to the boxes above
    and below.
    We only shrink if the box is close to the boxes above or below.

    We write the box layout unto the `layout` layer.

    Parameters
    ----------
    C: object
        Configuration settings
    stages: dict
        We need access to several intermediate results.
    stripes: list
        The preliminary stripe division of the page, as delivered by
        `getStripes`.
    batch: boolean
        Whether we run in batch mode.

    Returns
    -------
    dict
        Blocks keyed by stripe number and column specification
        (one of `""`, `"l"`, `"r"`).
        The values form dicts themselves, with in particular the bounding box
        information under key `box` specified as four numbers:
        left, top, right, bottom.

        The dict is ordered.
    """

    debug = C.debug
    marginX = C.blockMarginX
    blockColor = C.blockRGB
    letterColor = C.letterRGB
    rotated = stages["rotated"]
    normalized = stages["normalized"]

    (maxH, maxW) = normalized.shape[0:2]

    lineHeight = maxH // 10

    blocks = {}

    if not batch:
        layout = stages["layout"]
        imgOut = layout if debug > 1 else None

    for (stripe, (x, yMin, yMax)) in enumerate(stripes):

        yMinLee = max((0, yMin - lineHeight))
        yMaxLee = min((maxH, yMax + lineHeight))

        if x is None:
            (theYMin, theYMax) = adjustVertical(
                C, rotated, imgOut, 0, maxW, yMin, yMinLee, yMax, yMaxLee, False
            )
            blocks[(stripe, "")] = dict(
                box=(marginX, theYMin, maxW - marginX, theYMax), sep=x,
            )
            if not batch:
                cv2.rectangle(
                    layout,
                    (marginX, theYMin),
                    (maxW - marginX, theYMax),
                    blockColor,
                    4,
                )
                addStripe(layout, theYMin, 0, maxW, marginX, letterColor, stripe, "")
        else:
            (theYMinL, theYMaxL) = adjustVertical(
                C, rotated, imgOut, 0, x, yMin, yMinLee, yMax, yMaxLee, True
            )
            (theYMinR, theYMaxR) = adjustVertical(
                C, rotated, imgOut, x, maxW, yMin, yMinLee, yMax, yMaxLee, True
            )
            blocks[(stripe, "l")] = dict(
                box=(marginX, theYMinL, x - marginX, theYMaxL), sep=x
            )
            blocks[(stripe, "r")] = dict(
                box=(x + marginX, theYMinR, maxW - marginX, theYMaxR), sep=x
            )
            if not batch:
                cv2.rectangle(
                    layout, (marginX, theYMinL), (x - marginX, theYMaxL), blockColor, 4,
                )
                addStripe(layout, theYMinL, 0, x, marginX, letterColor, stripe, "l")
                cv2.rectangle(
                    layout,
                    (x + marginX, theYMinR),
                    (maxW - marginX, theYMaxR),
                    blockColor,
                    4,
                )
                addStripe(layout, theYMinR, x, maxW, marginX, letterColor, stripe, "r")
    return collections.OrderedDict(sorted(blocks.items()))


def applyHRules(C, stages, stretchesH, stripes, blocks, batch, boxed):
    """Trims regions above horizontal top lines and below bottom lines.

    Inspect the horizontal strokes and specifiy which ones are
    top separators and which ones are bottom separators.

    First we map each horizontal stretch to one of the page stripes.
    If a stretch occurs between stripes, we map it to the stripe above.

    A horizontal stroke is a top separator if
    *   it is mapped to the first stripe **and**
    *   it is situated in the top fragment of the page.

    We mark the discarded material on the layout page by overlaying
    it with gray.

    Parameters
    ----------
    C: object
        Configuration settings
    stages: dict
        We need access to several intermediate results.
    stretchesH: dict
        Horizontal line segments per y-coordinate, as delivered by `getStretches`.
    stripes: list
        The preliminary stripe division of the page, as delivered by
        `getStripes`.
    blocks: dict
        The blocks as delivered by `getBlocks`.
    boxed: boolean
        Whether we run in boxed mode (generate boxes around wiped marks).

    Returns
    -------
    None
        The blocks dict will be updated: each block value gets a new key `inner`
        with the bounding box info after stripping the top and bottom material.
    """

    mColor = C.marginRGB
    whit = C.whiteGRS
    white = C.whiteRGB
    letterColor = C.letterRGB
    normalized = stages["normalized"]
    demargined = normalized.copy()
    stages["demargined"] = demargined
    if not batch:
        layout = stages["layout"]
    if not batch or boxed:
        normalizedC = stages["normalizedC"]
        demarginedC = normalizedC.copy()
        stages["demarginedC"] = demarginedC

    (maxH, maxW) = normalized.shape[0:2]

    topCriterion = maxH / 6
    topXCriterion = maxH / 4

    for ((stripe, column), data) in blocks.items():
        (bL, bT, bR, bB) = data["box"]
        x = data["sep"]
        top = None
        bottom = None

        for (y, xs) in sorted(stretchesH.items()):
            if y < bT:
                continue
            if bB < y:
                break
            for (x1, x2, thickness) in xs:
                if x is not None:
                    if column == "l" and x1 >= x:
                        continue
                    if column == "r" and x2 <= x:
                        continue
                isTop = stripe == 0 and (
                    len(stripes) == 1
                    and y < topCriterion
                    or len(stripes) > 1
                    and y < topXCriterion
                )
                if isTop:
                    top = y + 2 * thickness + 2
                else:
                    if bottom is None:
                        bottom = y - 2 * thickness - 2
                if not batch:
                    addHStroke(
                        layout,
                        isTop,
                        stripe,
                        column,
                        thickness,
                        y,
                        x1,
                        x2,
                        letterColor,
                    )

        top = bT if top is None else top
        bottom = bB if bottom is None else bottom
        left = bL + 2
        right = bR - 2
        data["inner"] = (left, top, right, bottom)

        if top != bT:
            if not batch:
                overlay(layout, left, bT + 2, right, top, white, mColor)
            cv2.rectangle(demargined, (left, bT), (right, top), whit, -1)
            if not batch or boxed:
                overlay(demarginedC, left, bT + 2, right, top, white, mColor)
        if bottom != bB:
            if not batch:
                overlay(layout, left, bottom, right, bB - 2, white, mColor)
            cv2.rectangle(demargined, (left, bottom), (right, bB), whit, -1)
            if not batch or boxed:
                overlay(demarginedC, left, bottom, right, bB - 2, white, mColor)


def makeHistX(imgIn, left, top, right, bottom, imgOut=None):
    """Make a horizontal histogram of an input region of interest.

    Optionally draw the histograms on the corresponding roi of an output image.

    Parameters
    ----------
    imgIn: np array
        Input image.
    top, bottom, left, right: int
        Region of interest on input and output image.
    imgOut: np array, optional `None`
        Output image.

    Returns
    -------
    histX: list
        The X histogram
    """

    roiIn = imgIn[top:bottom, left:right]
    histX = cv2.reduce(roiIn, 0, cv2.REDUCE_AVG).reshape(-1)
    if imgOut is not None:
        roiOut = imgOut[top:bottom, left:right]
        for (i, val) in enumerate(histX):
            color = (int(val), int(2 * val), int(val))
            index = (i, 0)
            value = (i, val)
            cv2.line(roiOut, index, value, color, 1)

    return histX


def makeHistY(C, imgIn, left, top, right, bottom, imgOut=None, show=False):
    """Find the peaks in a vertical histogram.

    Optionally draw the histogram and the peaks
    on the corresponding roi of an output image.

    Parameters
    ----------
    imgIn: np array
        Input image.
    top, bottom, left, right: int
        Region of interest on input and output image.
    imgOut: np array, optional `None`
        Output image.

    Returns
    -------
    lines: list
        The detected lines, given as a tupple of upper and lower y coordinates
    """

    debug = C.debug

    if not debug:
        show = False
    white = C.whiteRGB
    black = C.blackRGB
    green = C.greenRGB
    mColor = C.marginRGB
    upperColor = C.upperRGB
    lowerColor = C.lowerRGB
    peakProminence = C.peakProminenceY
    valleyProminence = C.valleyProminenceY

    sqHWidth = 10
    sqWidth = 2 * sqHWidth
    sqDWidth = 4 * sqHWidth
    sqTWidth = 6 * sqHWidth

    (normH, normW) = (bottom - top, right - left)

    roiIn = imgIn[top:bottom, left:right]
    histY = cv2.reduce(roiIn, 1, cv2.REDUCE_AVG).reshape(-1)
    (peaks, peakData) = find_peaks(histY, prominence=peakProminence, distance=20)
    maxPeak = max(histY[peak] for peak in peaks)
    peakThreshold = 0.3 * maxPeak
    sigPeaks = [peak for peak in peaks if histY[peak] > peakThreshold]
    diffPeaks = [sigPeaks[i] - sigPeaks[i - 1] for i in range(1, len(sigPeaks))]
    if show:
        print("\nPeaks:")
        print(
            f"maxPeak={maxPeak}; {len(peaks)} peaks of which {len(sigPeaks)} > {peakThreshold}"
        )
        print(f"peaks={[f'{histY[peak]} @ {peak}' for peak in peaks]}")
        print(f"sigPeaks={sigPeaks}")
        print(f"diffPeaks={diffPeaks}")
    thisLineHeight = pureAverage(np.array(diffPeaks), C.lineHeight)
    C.lineHeight = thisLineHeight
    distance = int(round(0.5 * thisLineHeight))
    (peaks, peakData) = find_peaks(histY, prominence=2, distance=distance)

    histV = 255 - histY
    histV[0] = 0
    histV[-1] = 0
    (protoValleys, valleyData) = find_peaks(
        histV,
        prominence=valleyProminence,
        plateau_size=0,
        height=0,
        width=0,
        distance=distance,
    )
    if show:
        print("\nLines:")
    valleys = []
    for (
        i,
        (v, prominence, leftBase, rightBase, plateauSize, width, height),
    ) in enumerate(
        zip(
            protoValleys,
            valleyData["prominences"],
            valleyData["left_bases"],
            valleyData["right_bases"],
            valleyData["plateau_sizes"],
            valleyData["width_heights"],
            valleyData["peak_heights"],
        )
    ):
        rem = plateauSize + height < 240 or (
            plateauSize < 15 and width > 220 and height < 200
        )
        rem = prominence < 20 and plateauSize + height < 250
        if not rem:
            valleys.append(
                v + plateauSize // 3
                if i == 0
                else v - plateauSize // 3
                if i == len(protoValleys) - 1
                else v
            )
        if show:
            remRep = "xxx" if rem else f"{len(valleys):>3}"
            print(
                f"valley {remRep} @ {v:>4}"
                f" prom={int(round(prominence)):>3} l={leftBase:>4} r={rightBase:>4}"
                f" ps={plateauSize:>3}"
                f" w={int(round(width)):>3} h={int(round(height)):>3}"
            )

    lines = []
    lastV = 0
    lastLine = None
    for peak in peaks:
        while lastV < len(valleys) and valleys[lastV] <= peak:
            lastV += 1
        thisLine = (
            valleys[lastV - 1] if lastV > 0 else 0,
            valleys[lastV] if lastV < len(valleys) else normH,
        )
        if thisLine != lastLine:
            lines.append(thisLine)
            lastLine = thisLine

    if imgOut is not None:
        roiOut = imgOut[top:bottom, left:right]
        for (i, val) in enumerate(histY):
            color = (int(val), int(2 * val), int(val))
            index = (sqTWidth + 10, i)
            value = (sqTWidth + 10 + val, i)
            cv2.line(roiOut, index, value, color, 1)
        for e in valleys:
            index = (0, max((e - sqHWidth, 0)))
            value = (sqWidth, min((e + sqHWidth, len(histY) - 1)))
            cv2.rectangle(roiOut, index, value, black, -1)
        for e in peaks:
            index = (sqWidth, max((e - sqHWidth, 0)))
            value = (sqDWidth, min((e + sqHWidth, len(histY) - 1)))
            cv2.rectangle(roiOut, index, value, green, -1)
        # for e in sigPeaks:
        #    index = (sqDWidth, max((e - sqHWidth, 0)))
        #    value = (sqTWidth, min((e + sqHWidth, len(histY) - 1)))
        #    cv2.rectangle(roiOut, index, value, (0, 0, 255), -1)
        for (up, lo) in lines:
            overlay(roiOut, 14, up, normW - 14, up + 3, white, upperColor)
            overlay(roiOut, 14, lo - 3, normW - 14, lo, white, lowerColor)
        for (lo, up) in zip(
            (0, *(x[1] for x in lines)), (*(x[0] for x in lines), normH)
        ):
            overlay(roiOut, 14, lo, normW - 14, up + 1, white, mColor)

    return lines


def getHistograms(C, stages, blocks, batch, boxed):
    """Add line band data to all blocks based on histograms.

    By means of histograms we can discern where the lines are.
    We define several bands with respect to lines, such as main, inter, broad,
    high, mid, low.
    We also define a band for the space between lines.

    We mark the main bands on the `layout layer` by a starting green line
    and an ending red line and the space between them will be overlaid with gray.

    Parameters
    ----------
    C: object
        Configuration settings
    stages: dict
        We need access to several intermediate results.
    blocks: dict
        The blocks as delivered by `getBlocks`.
        The blocks dict will be updated: each block value gets a new key `bands`
        with the band data.
    batch: boolean
        Whether we run in batch mode.
    boxed: boolean
        Whether we run in boxed mode (generate boxes around wiped marks).

    Returns
    -------
    list
        A list of keys in the blocks dict that correspond to blocks
        that turn out to be devoid of written material.
    """

    mColor = C.marginRGB
    whit = C.marginGRS
    white = C.whiteRGB
    thresholdX = C.marginThresholdX
    colorBand = C.colorBand
    if not batch:
        layout = stages["layout"]
        histogram = layout.copy()
        stages["histogram"] = histogram

    rotated = stages["rotated"]
    demargined = stages["demargined"]

    emptyBlocks = []

    for ((stripe, column), data) in blocks.items():
        (left, top, right, bottom) = data["inner"]

        hasRegion = bottom > top and right > left

        if not hasRegion:
            emptyBlocks.append((stripe, column))
            continue

        imgOut = histogram if not batch else None
        histX = makeHistX(rotated, left, top, right, bottom, imgOut=imgOut)
        lines = makeHistY(
            C, rotated, left, top, right, bottom, imgOut=imgOut, show=True
        )

        # chop off the left and right margins of a region

        (normH, normW) = (bottom - top, right - left)
        roiOut = demargined[top:bottom, left:right]
        if not batch:
            roiOutC = layout[top:bottom, left:right]
        margins = getMargins(histX, normW, thresholdX)

        for (x1, x2) in margins:
            cv2.rectangle(roiOut, (x1, 0), (x2, normH), whit, -1)
            if not batch:
                overlay(roiOutC, x1 + 2, 2, x2 - 2, normH - 2, white, mColor)

        if len(margins) != 2:
            emptyBlocks.append((stripe, column))
            continue

        data["inner"] = (margins[0][1] + left, top, margins[1][0] + left, bottom)

        # define bands

        bands = {}
        data["bands"] = bands

        for (band, bandColor) in colorBand.items():
            inter = band in {"inter", "low", "high"}
            theLines = applyBandOffset(C, normH, band, lines, inter=inter)
            bands[band] = dict(lines=theLines, color=bandColor)

        bandInfo = bands["main"]
        lines = bandInfo["lines"]

        # remove top white space

        topWhite = lines[0][0] if lines else normH
        cv2.rectangle(roiOut, (0, 0), (normW, topWhite), whit, -1)
        if not batch:
            overlay(roiOutC, 0, 0, normW, topWhite, white, mColor)

        # remove bottom white space

        bottomWhite = lines[-1][1] if lines else 0
        cv2.rectangle(roiOut, (0, bottomWhite), (normW, normH), whit, -1)
        if not batch:
            overlay(roiOutC, 0, bottomWhite, normW, normH, white, mColor)

        if not lines:
            emptyBlocks.append((stripe, column))

    return emptyBlocks


def grayInterBlocks(C, stages, blocks, emptyBlocks):
    """Overlay the space between blocks with gray.

    Remove also the empty blocks from the block list.

    Parameters
    ----------
    C: object
        Configuration settings
    stages: dict
        We need access to several intermediate results.
    blocks: dict
        The blocks as delivered by `getBlocks`.
        The blocks dict will be updated: empty blocks will be deleted from it.
        with the band data.
    emptyBlocks: list
        The keys of blocks that do not have written content
        that must be processed further.

    Returns
    -------
    None.
    """

    mColor = C.marginRGB
    white = C.whiteRGB

    layout = stages["layout"]
    (maxH, maxW) = layout.shape[0:2]

    prevBB = [0, 0]
    prevX = None
    maxStripe = max(x[0] for x in blocks)
    marginX = C.blockMarginX

    # overlay the space between blocks

    for ((stripe, column), data) in sorted(blocks.items()):
        bT = data["box"][1]
        bB = data["box"][3]
        x = data["sep"]
        if column == "":
            if prevX is None:
                pB = prevBB[0]
                overlay(layout, marginX, pB, maxW - marginX, bT, white, mColor)
            else:
                for (i, pB) in enumerate(prevBB):
                    if pB < bT:
                        (lf, rt) = (
                            (marginX, prevX - marginX)
                            if i == 0
                            else (prevX + marginX, maxW - marginX)
                        )
                        overlay(layout, lf, pB, rt, bT, white, mColor)
            prevBB = [bB, bB]
            prevX = None
        elif column == "l":
            pB = prevBB[0]
            if pB < bT:
                overlay(layout, marginX, pB, x - marginX, bT, white, mColor)
            prevBB[0] = bB
            prevX = x
        elif column == "r":
            pB = prevBB[1]
            if pB < bT:
                overlay(layout, x + marginX, pB, maxW - marginX, bT, white, mColor)
            prevBB[1] = bB
            prevX = x
        if stripe == maxStripe:
            if column == "":
                if bB < maxH:
                    overlay(layout, marginX, bB, maxW - marginX, maxH, white, mColor)
            elif column == "l":
                if bB < maxH:
                    overlay(layout, marginX, bB, x - marginX, maxH, white, mColor)
            elif column == "r":
                if bB < maxH:
                    overlay(
                        layout, bB, maxW - marginX, maxH, white, x + marginX, mColor
                    )

    for b in emptyBlocks:
        del blocks[b]


def applyBandOffset(C, height, kind, lines, inter=False):
    offsetBand = C.offsetBand

    (top, bottom) = offsetBand[kind]

    def offset(x, off):
        x += off
        return 0 if x < 0 else height if x > height else x

    return tuple(
        (offset(up, top), offset(lo, bottom))
        for (up, lo) in (
            zip((x[1] for x in lines), (x[0] for x in lines[1:])) if inter else lines
        )
    )


def adjustVertical(
    C, rotated, layout, left, right, yMin, yMinLee, yMax, yMaxLee, preferExtend
):
    lines = makeHistY(C, rotated, left, yMinLee, right, yMaxLee, imgOut=None)
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
    topLee = yMin - yMinLee
    botLee = topLee + normH

    broadLines = applyBandOffset(C, normHLee, "broad", lines)

    if theYMin is None:
        if preferExtend:
            # look for the first lower boundary in the top of the strict region
            # then take the corresponding upper boundary
            for (i, (up, lo)) in enumerate(broadLines):
                if lo >= topLee:
                    theYMin = up
                    break
        else:
            # look for the first upper boundary in the top of the strict region
            for (up, lo) in broadLines:
                if up > topLee:
                    theYMin = up
                    break
        theYMin = yMin if theYMin is None else yMinLee + theYMin

    if theYMax is None:
        if preferExtend:
            # look for the last upper boundary in the bottom of the strict region
            # then take the corresponding lower boundary
            for (i, (up, lo)) in enumerate(reversed(broadLines)):
                if up <= botLee:
                    theYMax = lo
                    break
        else:
            # look for the last lower boundary in the bottom of the strict region
            for (up, lo) in reversed(broadLines):
                if lo < botLee:
                    theYMax = lo
                    break
        theYMax = yMax if theYMax is None else yMinLee + theYMax

    return (theYMin, theYMax)


def reborder(gray, bw, color, crop=False):
    """Add a border around a grayscale image, optionally remove white margins first.

    The border will add to the size of the image.

    Parameters
    ----------
    gray: np array
        A grayscale image.
    bw: int
        Width of the new border.
    color: int
        Color of the new border (grayscale).
    crop: boolean, optional `False`
        If `True`, the image will be cropped first such as to remove all surrounding
        white margins.
    """

    if crop:
        inv = 255 * (gray < 128).astype(np.uint8)
        coords = cv2.findNonZero(inv)
        x, y, w, h = cv2.boundingRect(coords)
        cropped = gray[y : y + h, x : x + w]
    else:
        cropped = gray
    bordered = cv2.copyMakeBorder(
        cropped, bw, bw, bw, bw, cv2.BORDER_CONSTANT, value=color
    )
    return bordered
    # Crop the image - note we do this on the original image


def pureAverage(data, supplied):
    """Get the average of a list of values after removing the outliers.

    It is used for calcaluting lineheights from a sequence of distances between
    histogram peaks.
    In practice, some peaks are missing due to short line lengths, and that
    causes some abnormal peak distances which we want to remove.

    Parameters
    ----------
    data: np array
        The list of values whose average we compute.
    """

    if data.size == 0:
        return supplied
    elif data.size == 1:
        return int(round(data[0]))

    # remove outliers
    m = 2.0
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.0
    pure = data[s < m]
    if len(pure) == 0:
        return supplied
    elif pure.size == 1:
        return int(round(pure[0]))
    return int(round(np.average(pure)))
