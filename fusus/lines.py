import cv2
import numpy as np
from scipy.signal import find_peaks, medfilt

from .lib import (
    applyBandOffset,
    getMargins,
    overlay,
    pureAverage,
)


def getInkDistribution(C, info, stages, pageH, blocks, batch, boxed):
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
    pageH: int
        size of a full page in pixels
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

    blurred = stages["blurred"]
    demargined = stages["demargined"]

    emptyBlocks = []

    for ((stripe, column), data) in blocks.items():
        (left, top, right, bottom) = data["inner"]

        hasRegion = bottom > top and right > left

        if not hasRegion:
            emptyBlocks.append((stripe, column))
            continue

        imgOut = histogram if not batch else None
        histX = getInkX(blurred, left, top, right, bottom, imgOut=imgOut)
        lines = getInkY(
            C, info, blurred, pageH, left, top, right, bottom, True, imgOut=imgOut
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


def getInkX(imgIn, left, top, right, bottom, imgOut=None):
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


def firstNonzero(arr, axis=None):
    return (arr != 0).argmax(axis=axis or 0)


def lastNonzero(arr, axis=None):
    ax = axis or 0
    mask = arr != 0
    ln = arr.shape[ax]
    val = ln - np.flip(mask, axis=ax or 0).argmax(axis=ax) - 1
    return val if axis is None else np.where(mask.any(axis=ax), val, -1)


def getHist(C, imgIn, lineHeight):
    if lineHeight is None:
        return cv2.reduce(imgIn, 1, cv2.REDUCE_AVG).reshape(-1)

    contourFactor = C.contourFactor
    contourOffset = C.contourOffset

    (h, w) = imgIn.shape[0:2]
    increase = int(round(w * contourOffset))

    left = firstNonzero(imgIn, axis=1)
    right = lastNonzero(imgIn, axis=1)

    left[left > increase] -= increase
    right[(0 < right) & (right < w - increase)] += increase

    # smooth the left and right contours by taking the median value
    # of a range around each value.
    # the range stretches a fraction of the peak distance to each side
    # we use a median filter from scipy for it

    windowSize = int(round(lineHeight * contourFactor))
    if not windowSize % 2:
        windowSize += 1
    if windowSize > 1:
        left = np.rint(medfilt(left, windowSize)).astype(int)
        right = np.rint(medfilt(right, windowSize)).astype(int)

    lengths = np.transpose(right - left + 1)

    histY = np.sum(imgIn, axis=1).astype(float)
    histY[lengths > 0] = histY[lengths > 0] / lengths[lengths > 0]
    histY[histY > 200] = 200
    return (np.rint(histY).astype(np.uint8), left, right)


def getInkY(C, info, imgIn, pageH, left, top, right, bottom, final, imgOut=None):
    """Determine the line distribution in a block of text.

    Optionally draw the histogram and the peaks and valleys
    on the corresponding roi of an output image.

    In this operation, we determine the regular line height by analysing the peaks
    and the distances between them.

    But if we have just one peak, we do not have distances.
    In those cases, we take the last line height that has been calculated.

    Parameters
    ----------
    C: object
        The configuration object of the book engine.
    info: function
        To write messages to the console
    imgIn: np array
        Input image.
    pageH: int
        size of a full page in pixels
    top, bottom, left, right: int
        Region of interest on input and output image.
    final: boolean
        When computing the layout of a page, we call this function
        to adjust the vertical sizes of blocks. This is a non-final call to this
        function. Later, we determine the lines per block, that is the final call.
        When debugging, it is handy to be able to distinguish the debug information
        generated by these calls.
    imgOut: np array, optional `None`
        Output image.

    Returns
    -------
    lines: list
        The detected lines, given as a list of tuples of upper and lower y coordinates
    """

    debug = C.debug
    show = debug > 1 or debug == 1 and final

    white = C.whiteRGB
    black = C.blackRGB
    green = C.greenRGB
    orange = C.orangeRGB
    purple = C.purpleRGB
    mColor = C.marginRGB
    upperColor = C.upperRGB
    lowerColor = C.lowerRGB
    peakSignificant = C.peakSignificant
    peakTargetWidthFraction = C.peakTargetWidthFraction
    peakProminence = C.peakProminenceY
    valleyProminence = C.valleyProminenceY
    outerValleyShiftFraction = C.outerValleyShiftFraction
    defaultLineHeight = C.defaultLineHeight

    peakDistance = int(round(pageH / 45))

    # little squares that indicate the significant peaks and valleys in the histogram
    sqHWidth = 10
    sqWidth = 2 * sqHWidth
    sqDWidth = 4 * sqHWidth

    (normH, normW) = (bottom - top, right - left)

    roiIn = imgIn[top:bottom, left:right]

    # the raw histogram
    histY = getHist(C, roiIn, None)

    # estimate the lineheight based on the raw histogram

    def getLineHeight(histY, show=False):
        # rough collection of peaks (we'll find too many)
        (peaks, peakData) = find_peaks(
            histY, prominence=peakProminence, distance=peakDistance
        )

        # if there are no peaks: no lines

        if not len(peaks):
            return None

        # filter out the significant peaks
        maxPeak = max(histY[peak] for peak in peaks)
        peakThreshold = peakSignificant * maxPeak
        sigPeaks = [peak for peak in peaks if histY[peak] > peakThreshold]

        # get the distances between the significant peaks
        diffPeaks = [sigPeaks[i] - sigPeaks[i - 1] for i in range(1, len(sigPeaks))]
        if show:
            info("\nPeaks:", tm=False)
            info(
                f"maxPeak={maxPeak};"
                f" {len(peaks)} peaks of which {len(sigPeaks)} > {peakThreshold}",
                tm=False,
            )
            info("Peaks:")
            for peak in peaks:
                info(f"{histY[peak]:>3} @ {peak:>4}", tm=False)
            info(f"sigPeaks={sigPeaks}", tm=False)
            info(f"diffPeaks={diffPeaks}", tm=False)

        # remove the outliers from the distances and determine the average of the
        # remaining distances: that is the line height
        return pureAverage(np.array(diffPeaks), defaultLineHeight)

    lineHeight = getLineHeight(histY, show=False)
    if lineHeight is None:
        # no lines
        return []

    # compute a better histogram, based on smooth contour lines
    # Crucial: the contour computation is based on the estimated line height
    (histY, leftContour, rightContour) = getHist(C, roiIn, lineHeight)
    lineHeight = getLineHeight(histY, show=show)
    if lineHeight is None:
        # no lines
        return []

    # precise calculation of peaks, based on the calculated line height
    distance = int(round(peakTargetWidthFraction * lineHeight))
    plateauThreshold = int(distance // 4)
    (peaks, peakData) = find_peaks(histY, prominence=2, distance=distance)

    # invert the histogram data to detect valleys
    histV = 255 - histY

    # let the inverted histogram start and end with zeroes,
    # otherwise the first and last peaks in the inverted histogram are not detected.
    # These are the first and last valleys of the original histogram.
    # The find_peaks() algorithm in SciPy does not detect one-sided peaks, i.e.
    # peaks right at the start or the end of a sequence.
    histV[0] = 0
    histV[-1] = 0

    # Rough way to find the valleys.
    # It turns out that we find too many valleys, and when we increase the prominence,
    # we miss important valleys.
    (protoValleys, valleyData) = find_peaks(
        histV,
        prominence=valleyProminence,
        distance=distance,
        plateau_size=0,
        height=0,
        width=0,
    )
    if show:
        info("\nLines:", tm=False)

    # We need to filter by a rather subtle criterion, involving the plateau size,
    # height, and width of a peak.
    # for valleys with a big plateau, we split them into two ones, closer to
    # the ink, one higher, one lower than the plateau.

    valleys = []
    remove = None

    def showValley(v):
        removeRep = "xxx" if remove else f"{len(valleys):>3}"
        info(
            f"valley {removeRep} @ {v:>4}"
            f" prom={int(round(prominence)):>3}"
            f" ps={plateauSize:>3}"
            f" w={int(round(width)):>3} h={int(round(height)):>3}",
            tm=False,
        )

    for (i, (v, prominence, plateauSize, width, height),) in enumerate(
        zip(
            protoValleys,
            valleyData["prominences"],
            valleyData["plateau_sizes"],
            valleyData["width_heights"],
            valleyData["peak_heights"],
        )
    ):
        # a valley with a smallish prominence and small plateau combined
        # with a lack of depth is not convincing

        # the valleys at the start and at the end might be too far removed
        # from the actual ink.
        # We recognize that by means of the size of the plateau.
        # Therefore we shift the valley towards the ink over a length
        # proportional to the plateau size.

        remove = prominence < 50 or (prominence < 100 and (plateauSize + height < 230))
        lastProtoValley = len(protoValleys) - 1
        if i == 0 or i == lastProtoValley:
            shiftCorrection = int(plateauSize * outerValleyShiftFraction)
            vc = v + shiftCorrection if i == 0 else v - shiftCorrection
            if not remove:
                valleys.append(vc)
            if show:
                showValley(vc)
        else:
            if plateauSize > 2 * plateauThreshold:
                thisShift = int(plateauSize // 2) - plateauThreshold
                if not remove:
                    valleys.append(v - thisShift)
                if show:
                    showValley(v - thisShift)
                if not remove:
                    valleys.append(v + thisShift)
                if show:
                    showValley(v + thisShift)
            else:
                if not remove:
                    valleys.append(v)
                if show:
                    showValley(v)

    # from the peaks and valleys found above, compute the lines
    # as a list of (top, bottom) coordinates.

    # For each peak we determine its nearest surrounding valleys before and after.
    # Those are the top and bottom of a line.
    # It is possible that there are multiple peaks between valleys.
    # We take care to not produce duplicate lines in these cases.

    # We walk through the peaks and maintain the last relevant valley.

    lines = []
    lastV = 0
    lastLine = None
    for peak in peaks:
        # move forward the last valley until it passes the peak
        while lastV < len(valleys) and valleys[lastV] <= peak:
            lastV += 1
        # then the valley before lastV is the last valley before the peak,
        # and lastV itself is the first valley after the peak
        thisLine = (
            valleys[lastV - 1] if lastV > 0 else 0,
            valleys[lastV] if lastV < len(valleys) else normH,
        )
        # we found a line.
        # Check that it is not the same line that we found before.
        # If all is well, add it to the result.
        if thisLine != lastLine:
            lines.append(thisLine)
            lastLine = thisLine

    if imgOut is not None:
        roiOut = imgOut[top:bottom, left:right]
        faze = 5
        for (i, val) in enumerate(leftContour):
            tl = (max((val - faze, 0)), max((i - faze, 0)))
            br = (min((val + faze, right)), min((i + faze, bottom)))
            cv2.rectangle(roiOut, tl, br, orange, -1)
        for (i, val) in enumerate(rightContour):
            tl = (max((val - faze, 0)), max((i - faze, 0)))
            br = (min((val + faze, right)), min((i + faze, bottom)))
            cv2.rectangle(roiOut, tl, br, purple, -1)
        for (i, val) in enumerate(histY):
            color = (int(val), int(2 * val), int(val))
            index = (sqDWidth + 10, i)
            value = (sqDWidth + 10 + val, i)
            cv2.line(roiOut, index, value, color, 1)
        for e in valleys:
            index = (0, max((e - sqHWidth, 0)))
            value = (sqWidth, min((e + sqHWidth, len(histY) - 1)))
            cv2.rectangle(roiOut, index, value, black, -1)
        for e in peaks:
            index = (sqWidth, max((e - sqHWidth, 0)))
            value = (sqDWidth, min((e + sqHWidth, len(histY) - 1)))
            cv2.rectangle(roiOut, index, value, green, -1)
        for (up, lo) in lines:
            overlay(roiOut, 14, up, normW - 14, up + 3, white, upperColor)
            overlay(roiOut, 14, lo - 3, normW - 14, lo, white, lowerColor)
        for (lo, up) in zip(
            (0, *(x[1] for x in lines)), (*(x[0] for x in lines), normH)
        ):
            overlay(roiOut, 14, lo, normW - 14, up + 1, white, mColor)

    return lines
