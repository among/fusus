"""Detect the page layout.

Pages consist of a header region, a body region, and a footer region, all of which
are optional.


**header**
The header consists of a caption and/or a page number.
All headers will be discarded.

**footer**
The footer consists of footnote bodies.
All footers will be discarded.

**body**
The body region consists of zero or more *stripes*.

**stripe, block, line**
A stripe is a horizontal region of the body.
If some parts of the body have two blocks and other parts have one block,
we divide the body in stripes where each stripe has a fixed number of blocks,
and neighbouring stripes have a different number of blocks.

If the whole body has the same number of blocks, we have just one stripe.

The stripes are numbered 1, 2, 3, ... from top to bottom.

The block is the empty string if a stripe has just one block,
otherwise it is `l` for the left block and `r` for the right block.

We assume that all stripes on all pages have at most two blocks.

Blocks are divided into *lines*.
The lines are numbered with the blocks that contain them.
"""

import collections
import cv2

from tf.core.helpers import rangesFromSet

from .lib import (
    applyBandOffset,
    FONT,
    findRuns,
    overlay,
    showImage,
)

from .lines import getInkY


def addBlockName(img, top, left, right, marginX, letterColor, stripe, kind, size=1.0):
    """Adds the name of a block of the page near the block.

    The function `fusus.page.Page.doLayout` divides the page into blocks.
    This function puts the name of each block on the image, positioned
    suitably w.r.t. the block.

    Parameters
    ----------
    img: image as np array
        the image to operate on
    top, left, right: integer
        Where the top, left, right edges of the image are.
    marginX: integer
        Where we set the left margin
    letterColor: color
        The color of the letters
    stripe: integer
        The stripe number. Stripes are horizontal page-wide regions corresponding
        to *vertical* block dividers.
    kind: string
        Whether the block spans the whole page width (`""`), is in the left block
        ("l") or in the right block ("r").
    size: float
        The font-size of the letters.

    Returns
    -------
    None
        The source image receives a modification.
    """

    weight = 3
    offsetX = 80 + marginX
    halfOffsetX = int(offsetX // 2)
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
    img, isTop, i, block, thickness, top, left, right, letterColor, size=1.0
):
    """Marks a detected horizontal stroke on an image.

    The layout algorithm detects horizontal strokes.
    For feedback to the user, we draw a frame around the detected strokes and give
    them a name.

    Parameters
    ----------
    img: image as np array
        the image to operate on
    isTop: boolean
        whether the stroke separates the top header from the rest of the page.
    i: integer
        The number of the stroke
    block: string {"l", "r", ""}
        The block in which the stroke is found
    thickness: integer
        The thickness of the stroke as found on the image.
    top, left, right: integer
        Where the top, left, right edges of the image are.
    letterColor: color
        The color of the letters
    size: float
        The font-size of the letters.

    Returns
    -------
    None
        The source image receives a modification.
    """

    weight = 3
    colRep = f"-{block}" if block else ""
    text = f"{'T' if isTop else 'B'}{i}{colRep}"
    offsetX = 60
    offsetY = 30 if isTop else -30 - 2 * thickness
    x = int(left + (right - left - offsetX) // 2)
    y = top - offsetY

    cv2.putText(
        img,
        text,
        (x, y),
        FONT,
        size,
        letterColor,
        weight,
        cv2.LINE_AA,
    )


def getStretches(C, info, stages, pageSize, horizontal, batch):
    """Gets significant horizontal or vertical strokes.

    Significant strokes are those that are not part of letters,
    but ones that are used as separators, e.g. of footnotes and blocks.

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
        To write messages to the console
    stages: dict
        Intermediate cv2 images, keyed by stage name
    pageSize: int
        The width or height in pixels of a complete page. Note that
        the image we work with, might be a fraction of a page
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

    minLength = int(pageSize // 30 if horizontal else pageSize // 50)
    afterLength = int(pageSize // 10 if horizontal else pageSize // 17)

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
        middle = int((b + e) // 2)
        thickness = int((abs(e - b) + 1) // 2)
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


def getBlocks(C, info, stages, pageH, stripes, stretchesH, batch):
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
    We do not grow boxes across significant horizontal strokes.

    We write the box layout unto the `layout` layer.

    Parameters
    ----------
    C: object
        Configuration settings
    stages: dict
        We need access to several intermediate results.
    pageH: int
        The height of a full page in pixels (the image might be a fraction of a page)
    stripes: list
        The preliminary stripe division of the page, as delivered by
        `getStripes`.
    stretchesH: list
        The horizontal stretches across which we do not shrink of enlarge
    batch: boolean
        Whether we run in batch mode.

    Returns
    -------
    dict
        Blocks keyed by stripe number and block specification
        (one of `""`, `"l"`, `"r"`).
        The values form dicts themselves, with in particular the bounding box
        information under key `box` specified as four numbers:
        left, top, right, bottom.

        The dict is ordered.
    """

    marginX = C.blockMarginX
    blockColor = C.blockRGB
    letterColor = C.letterRGB
    blurred = stages["blurred"]
    normalized = stages["normalized"]

    (maxH, maxW) = normalized.shape[0:2]

    leeHeight = int(pageH // 20)

    blocks = {}

    upperHStretch = min(stretchesH) if stretchesH else 0
    lowerHStretch = max(stretchesH) if stretchesH else maxH

    if not batch:
        layout = stages["layout"]

    for (stripe, (x, yMin, yMax)) in enumerate(stripes):

        yMinLee = max((0, yMin - leeHeight))
        yMaxLee = min((maxH, yMax + leeHeight))

        if x is None:
            (theYMin, theYMax) = adjustVertical(
                C, info, blurred, pageH, 0, maxW, yMin, yMinLee, yMax, yMaxLee, False
            )
            blocks[(stripe, "")] = dict(
                box=(marginX, theYMin, maxW - marginX, theYMax),
                sep=x,
            )
            if not batch:
                cv2.rectangle(
                    layout,
                    (marginX, theYMin),
                    (maxW - marginX, theYMax),
                    blockColor,
                    4,
                )
                addBlockName(layout, theYMin, 0, maxW, marginX, letterColor, stripe, "")
        else:
            yMinLeeBound = (
                yMinLee
                if upperHStretch == 0 or upperHStretch > yMin
                else max((yMinLee, max(y for y in stretchesH if y <= yMin)))
            )
            yMaxLeeBound = (
                yMaxLee
                if lowerHStretch == maxH or lowerHStretch < yMax
                else min((yMaxLee, min(y for y in stretchesH if y >= yMax)))
            )
            (theYMinL, theYMaxL) = adjustVertical(
                C,
                info,
                blurred,
                pageH,
                0,
                x,
                yMin,
                yMinLeeBound,
                yMax,
                yMaxLeeBound,
                True,
            )
            (theYMinR, theYMaxR) = adjustVertical(
                C,
                info,
                blurred,
                pageH,
                x,
                maxW,
                yMin,
                yMinLeeBound,
                yMax,
                yMaxLeeBound,
                True,
            )
            blocks[(stripe, "l")] = dict(
                box=(marginX, theYMinL, x - marginX, theYMaxL), sep=x
            )
            blocks[(stripe, "r")] = dict(
                box=(x + marginX, theYMinR, maxW - marginX, theYMaxR), sep=x
            )
            if not batch:
                cv2.rectangle(
                    layout,
                    (marginX, theYMinL),
                    (x - marginX, theYMaxL),
                    blockColor,
                    4,
                )
                addBlockName(layout, theYMinL, 0, x, marginX, letterColor, stripe, "l")
                cv2.rectangle(
                    layout,
                    (x + marginX, theYMinR),
                    (maxW - marginX, theYMaxR),
                    blockColor,
                    4,
                )
                addBlockName(
                    layout, theYMinR, x, maxW, marginX, letterColor, stripe, "r"
                )
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

    for ((stripe, block), data) in blocks.items():
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
                    if block == "l" and x1 >= x:
                        continue
                    if block == "r" and x2 <= x:
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
                        block,
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


def grayInterBlocks(C, stages, blocks):
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

    for ((stripe, block), data) in sorted(blocks.items()):
        bT = data["box"][1]
        bB = data["box"][3]
        x = data["sep"]
        if block == "":
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
        elif block == "l":
            pB = prevBB[0]
            if pB < bT:
                overlay(layout, marginX, pB, x - marginX, bT, white, mColor)
            prevBB[0] = bB
            prevX = x
        elif block == "r":
            pB = prevBB[1]
            if pB < bT:
                overlay(layout, x + marginX, pB, maxW - marginX, bT, white, mColor)
            prevBB[1] = bB
            prevX = x
        if stripe == maxStripe:
            if block == "":
                if bB < maxH:
                    overlay(layout, marginX, bB, maxW - marginX, maxH, white, mColor)
            elif block == "l":
                if bB < maxH:
                    overlay(layout, marginX, bB, x - marginX, maxH, white, mColor)
            elif block == "r":
                if bB < maxH:
                    overlay(
                        layout, bB, maxW - marginX, maxH, white, x + marginX, mColor
                    )


def adjustVertical(
    C, info, blurred, pageH, left, right, yMin, yMinLee, yMax, yMaxLee, preferExtend
):
    """Adjust the height of blocks.

    When we determine the vertical sizes of blocks from the vertical block separators
    on the page, we may find that these separators are too short.

    We remedy this by finding the line divisision of the ink left and right from the
    dividing line, and enlarging the blocks left and right so that they contain
    complete lines.

    Parameters
    ----------
    C: object
        Configuration settings
    info: function
        To write messages to the console
    blurred: image as np array
        The input image. It must be the `blurred` stage of the source image,
        which is blurred and inverted.
    pageH: int
        size of a full page in pixels
    left, right: int
        The left and right edges of the block
    yMin: integer
        the initial top edge of the block
    yMinLee: integer
        the top edge of the block when the leeway is applied
    yMax: integer
        the initial bottom edge of the block
    yMaxLee: integer
        the bottom edge of the block when the leeway is applied
    preferExtend: boolean
        Whether we want to increase or rather decrease the vertical size of the block.
        Blocks next to dividing lines are meant to be increased, blocks that
        span the whole page width are meant to be decreased.

    Returns
    -------
    tuple
        The corrected top and bottom heights of the block.
    """

    theYMin = None
    theYMax = None

    if yMin == yMinLee:
        theYMin = yMin
    if yMax == yMaxLee:
        theYMax = yMax
    if theYMin is not None and theYMax is not None:
        return (theYMin, theYMax)

    lines = getInkY(
        C, info, blurred, pageH, left, yMinLee, right, yMaxLee, False, imgOut=None
    )
    normHLee = yMaxLee - yMinLee
    topProper = yMin - yMinLee
    botProper = yMax - yMinLee

    normLines = applyBandOffset(C, normHLee, "main", lines)

    if theYMin is None:
        if preferExtend:
            # look for the first lower boundary in the top of the strict region
            # then take the corresponding upper boundary
            for (i, (up, lo)) in enumerate(normLines):
                if up <= topProper and lo >= topProper:
                    theYMin = up + yMinLee
                    break
        else:
            # look for the first upper boundary in the top of the strict region
            for (up, lo) in normLines:
                if up >= topProper and lo <= botProper:
                    theYMin = up + yMinLee
                    break
        if theYMin is None:
            theYMin = yMin

    if theYMax is None:
        if preferExtend:
            # look for the last upper boundary in the bottom of the strict region
            # then take the corresponding lower boundary
            for (i, (up, lo)) in enumerate(reversed(normLines)):
                if up <= botProper and lo >= botProper:
                    theYMax = lo + yMinLee
                    break
        else:
            # look for the last lower boundary in the bottom of the strict region
            for (up, lo) in reversed(normLines):
                if lo <= botProper and up >= topProper:
                    theYMax = lo + yMinLee
                    break
        if theYMax is None:
            theYMax = yMax

    return (theYMin, theYMax)
