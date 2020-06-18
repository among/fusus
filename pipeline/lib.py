import os
import io
from itertools import chain, groupby
from tempfile import NamedTemporaryFile

import numpy as np
import PIL.Image
from IPython.display import HTML, Image, display
import cv2

from tf.core.helpers import rangesFromList, specFromRanges

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


def pagesRep(source):
    pages = [int(splitext(f)[0].lstrip("0")) for f in source]
    return specFromRanges(rangesFromList(pages))


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


def connected(markH, markW, bw, threshold, gray, hitPoint):
    (textH, textW) = gray.shape
    (hitY, hitX) = hitPoint

    # print(hitPoint)
    connDegree = 0
    nparts = 0

    realBw = min((bw, markW, markH))

    # left boundary

    fo = max((0, hitX - realBw)) if hitX > 0 else None
    if fo is not None:
        to = hitX
        texto = np.array(
            (255 - gray[hitY : hitY + markH, fo:to]).max(axis=1), dtype=np.uint16
        )
        fi = hitX
        ti = hitX + realBw
        texti = np.array(
            (255 - gray[hitY : hitY + markH, fi:ti]).max(axis=1), dtype=np.uint16
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
    if to is not None:
        fo = hitX + markW
        texto = np.array(
            (255 - gray[hitY : hitY + markH, fo:to]).max(axis=1), dtype=np.uint16
        )
        fi = hitX + markW - realBw
        ti = hitX + markW
        texti = np.array(
            (255 - gray[hitY : hitY + markH, fi:ti]).max(axis=1), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        connDegree += val
        nparts += 1

    # top boundary

    f = max((0, hitY - realBw)) if hitY > 0 else None
    if f is not None:
        t = hitY
        texto = np.array(
            (255 - gray[f:t, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
        )
        fi = hitY
        ti = hitY + realBw + 1
        texti = np.array(
            (255 - gray[fi:ti, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
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
    if t is not None:
        f = hitY + markH
        texto = np.array(
            (255 - gray[f:t, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
        )
        ti = hitY + markH
        fi = hitY + markH - realBw
        texti = np.array(
            (255 - gray[fi:ti, hitX : hitX + markW]).max(axis=0), dtype=np.uint16
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
        im,
        top,
        bottom,
        left,
        right,
        border,
        fillN,
        band,
        seq,
        connDegree,
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


def getLargest(hist, width, threshold):
    """Get biggest chunk of nonzero values

    Chunks are consecutive indices of a source array whose values count as nonzero.
    After chunking a source array, we compute the chunk with width greater than half
    of the source array, if such a chunk exists. And then we deliver
    everything outside that chunk.

    Otherwise we deliver all values from the source array that count as zero.

    Parameters
    ----------
    hist: [int]
        Source array of pixel values
    width: int
        Maximum index of the source array
    threshold: int
        Value below which pixels count as zero
    """
    result = None
    for chunk in (
        [i for (i, value) in it]
        for (key, it) in groupby(enumerate(hist), key=lambda x: x[1] >= threshold)
        if key >= threshold
    ):
        if len(chunk) > width / 2:
            result = list(chain(range(chunk[0]), range(chunk[-1] + 1, width)))
            break
    if result is None:
        result = [i for (i, value) in enumerate(hist) if value < threshold]
    return result


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
