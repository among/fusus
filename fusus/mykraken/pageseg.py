# -*- coding: utf-8 -*-
#
# Copyright 2015 Benjamin Kiessling
#           2014 Thomas M. Breuel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing
# permissions and limitations under the License.

# Modified by Dirk Roorda (2020)
# - we supply images in array format, no need to convert to and from PIL
# - the input image is always binarized
# - we do not need rotation for vertical scripts
# - no mask and pad  parameters

"""
kraken.pageseg
~~~~~~~~~~~~~~

Layout analysis and script detection methods.
"""
import numpy as np

from typing import Tuple, List, Callable, Optional, Dict, Any
from scipy.ndimage.filters import gaussian_filter, uniform_filter, maximum_filter

from kraken.lib import morph, sl
from kraken.lib.segmentation import reading_order, topsort


class record(object):
    """
    Simple dict-like object.
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.label = 0  # type: int
        self.bounds = []  # type: List
        self.mask = None  # type: np.array


def find(condition):
    "Return the indices where ravel(condition) is true"
    (res,) = np.nonzero(np.ravel(condition))
    return res


def binary_objects(binary: np.array) -> np.array:
    """
    Labels features in an array and segments them into objects.
    """
    labels, _ = morph.label(binary)
    objects = morph.find_objects(labels)
    return objects


def estimate_scale(binary: np.array) -> float:
    """
    Estimates image scale based on number of connected components.
    """
    objects = binary_objects(binary)
    bysize = sorted(objects, key=sl.area)
    scalemap = np.zeros(binary.shape)
    for o in bysize:
        if np.amax(scalemap[o]) > 0:
            continue
        scalemap[o] = sl.area(o) ** 0.5
    scale = np.median(scalemap[(scalemap > 3) & (scalemap < 100)])
    return scale


def compute_boxmap(
    binary: np.array,
    scale: float,
    threshold: Tuple[float, int] = (0.5, 4),
    dtype: str = "i",
) -> np.array:
    """
    Returns grapheme cluster-like boxes based on connected components.
    """
    objects = binary_objects(binary)
    bysize = sorted(objects, key=sl.area)
    boxmap = np.zeros(binary.shape, dtype)
    for o in bysize:
        if sl.area(o) ** 0.5 < threshold[0] * scale:
            continue
        if sl.area(o) ** 0.5 > threshold[1] * scale:
            continue
        boxmap[o] = 1
    return boxmap


def compute_lines(segmentation, scale):
    """Given a line segmentation map, computes a list
    of tuples consisting of 2D slices and masked images."""

    # Convert segmentation to lines
    lobjects = morph.find_objects(segmentation)
    lines = []
    for i, o in enumerate(lobjects):
        if o is None:
            continue
        if sl.dim1(o) < 2 * scale or sl.dim0(o) < scale:
            continue
        mask = segmentation[o] == i + 1
        if np.amax(mask) == 0:
            continue
        result = record()
        result.label = i + 1
        result.bounds = o
        result.mask = mask
        lines.append(result)
    return lines


def compute_separators_morph(
    binary: np.array, scale: float, sepwiden: int = 10, maxcolseps: int = 2
) -> np.array:
    """Finds vertical black lines corresponding to column separators."""

    # Finding vertical black column lines
    d0 = int(max(5, scale / 4))
    d1 = int(max(5, scale)) + sepwiden
    thick = morph.r_dilation(binary, (d0, d1))
    vert = morph.rb_opening(thick, (10 * scale, 1))
    vert = morph.r_erosion(vert, (d0 // 2, sepwiden))
    vert = morph.select_regions(vert, sl.dim1, min=3, nbest=2 * maxcolseps)
    vert = morph.select_regions(vert, sl.dim0, min=20 * scale, nbest=maxcolseps)
    return vert


def compute_colseps_conv(
    binary: np.array, scale: float = 1.0, minheight: int = 10, maxcolseps: int = 2
) -> np.array:
    """Find column separators by convolution and thresholding.

    Args:
        binary (numpy.array):
        scale (float):
        minheight (int):
        maxcolseps (int):

    Returns:
        Separators
    """

    # Finding max {maxcolseps} column separators
    # find vertical whitespace by thresholding
    smoothed = gaussian_filter(1.0 * binary, (scale, scale * 0.5))
    smoothed = uniform_filter(smoothed, (5.0 * scale, 1))
    thresh = smoothed < np.amax(smoothed) * 0.1
    # find column edges by filtering
    grad = gaussian_filter(1.0 * binary, (scale, scale * 0.5), order=(0, 1))
    grad = uniform_filter(grad, (10.0 * scale, 1))
    grad = grad > 0.5 * np.amax(grad)
    # combine edges and whitespace
    seps = np.minimum(thresh, maximum_filter(grad, (int(scale), int(5 * scale))))
    seps = maximum_filter(seps, (int(2 * scale), 1))
    # select only the biggest column separators
    seps = morph.select_regions(seps, sl.dim0, min=minheight * scale, nbest=maxcolseps)
    return seps


def compute_black_colseps(
    binary: np.array, scale: float, maxcolseps: int
) -> Tuple[np.array, np.array]:
    """
    Computes column separators from vertical black lines.

    Args:
        binary (numpy.array): Numpy array of the binary image
        scale (float):

    Returns:
        (colseps, binary):
    """

    # Extract vertical black column separators from lines
    seps = compute_separators_morph(binary, scale, maxcolseps)
    colseps = np.maximum(
        compute_colseps_conv(binary, scale, maxcolseps=maxcolseps), seps
    )
    binary = np.minimum(binary, 1 - seps)
    return colseps, binary


def compute_white_colseps(
    binary: np.array, scale: float, maxcolseps: int
) -> Tuple[np.array, np.array]:
    """
    Computes column separators either from vertical black lines or whitespace.

    Args:
        binary (numpy.array): Numpy array of the binary image
        scale (float):

    Returns:
        colseps:
    """
    return compute_colseps_conv(binary, scale, maxcolseps=maxcolseps)


def norm_max(v: np.array) -> np.array:
    """
    Normalizes the input array by maximum value.
    """
    return v / np.amax(v)


def compute_gradmaps(binary: np.array, scale: float, gauss: bool = False):
    """
    Use gradient filtering to find baselines

    Args:
        binary (numpy.array):
        scale (float):
        gauss (bool): Use gaussian instead of uniform filtering

    Returns:
        (bottom, top, boxmap)
    """
    # use gradient filtering to find baselines

    # Computing gradient maps
    boxmap = compute_boxmap(binary, scale)
    cleaned = boxmap * binary
    if gauss:
        grad = gaussian_filter(1.0 * cleaned, (0.3 * scale, 6 * scale), order=(1, 0))
    else:
        grad = gaussian_filter(
            1.0 * cleaned, (max(4, 0.3 * scale), scale), order=(1, 0)
        )
        grad = uniform_filter(grad, (1, 6 * scale))
    bottom = norm_max((grad < 0) * (-grad))
    top = norm_max((grad > 0) * grad)
    return bottom, top, boxmap


def compute_line_seeds(
    binary: np.array,
    bottom: np.array,
    top: np.array,
    colseps: np.array,
    scale: float,
    threshold: float = 0.2,
) -> np.array:
    """
    Base on gradient maps, computes candidates for baselines and xheights.
    Then, it marks the regions between the two as a line seed.
    """

    # Finding line seeds
    vrange = int(scale)
    bmarked = maximum_filter(bottom == maximum_filter(bottom, (vrange, 0)), (2, 2))
    bmarked = (
        bmarked * (bottom > threshold * np.amax(bottom) * threshold) * (1 - colseps)
    )
    tmarked = maximum_filter(top == maximum_filter(top, (vrange, 0)), (2, 2))
    tmarked = tmarked * (top > threshold * np.amax(top) * threshold / 2) * (1 - colseps)
    tmarked = maximum_filter(tmarked, (1, 20))
    seeds = np.zeros(binary.shape, "i")
    delta = max(3, int(scale / 2))
    for x in range(bmarked.shape[1]):
        transitions = sorted(
            [(y, 1) for y in find(bmarked[:, x])]
            + [(y, 0) for y in find(tmarked[:, x])]
        )[::-1]
        transitions += [(0, 0)]
        for i in range(len(transitions) - 1):
            y0, s0 = transitions[i]
            if s0 == 0:
                continue
            seeds[y0 - delta : y0, x] = 1
            y1, s1 = transitions[i + 1]
            if s1 == 0 and (y0 - y1) < 5 * scale:
                seeds[y1:y0, x] = 1
    seeds = maximum_filter(seeds, (1, int(1 + scale)))
    seeds = seeds * (1 - colseps)
    seeds, _ = morph.label(seeds)
    return seeds


def remove_hlines(binary: np.array, scale: float, maxsize: int = 10) -> np.array:
    """
    Removes horizontal black lines that only interfere with page segmentation.

        Args:
            binary (numpy.array):
            scale (float):
            maxsize (int): maximum size of removed lines

        Returns:
            numpy.array containing the filtered image.

    """

    # Filtering horizontal lines
    labels, _ = morph.label(binary)
    objects = morph.find_objects(labels)
    for i, b in enumerate(objects):
        if sl.width(b) > maxsize * scale:
            labels[b][labels[b] == i + 1] = 0
    return np.array(labels != 0, "B")


def rotate_lines(lines: np.array, angle: float, offset: int) -> np.array:
    """
    Rotates line bounding boxes around the origin and adding and offset.
    """

    # Rotate line coordinates by {angle} with offset {offset}
    angle = np.radians(angle)
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    p = np.array(lines).reshape((-1, 2))
    offset = np.array([2 * offset])
    p = p.dot(r).reshape((-1, 4)).astype(int) + offset
    x = np.sort(p[:, [0, 2]])
    y = np.sort(p[:, [1, 3]])
    return np.column_stack((x.flatten(), y.flatten())).reshape(-1, 4)


def segment(
    raw,
    text_direction: str = "horizontal-lr",
    scale: Optional[float] = None,
    maxcolseps: float = 2,
    black_colseps: bool = False,
    no_hlines: bool = True,
    reading_order_fn: Callable = reading_order,
) -> Dict[str, Any]:
    """
    Segments a page into text lines.

    Segments a page into text lines and returns the absolute coordinates of
    each line in reading order.

    Args:
        im (PIL.Image): A bi-level page of mode '1' or 'L'
        text_direction (str): Principal direction of the text
                              (horizontal-lr/rl/vertical-lr/rl)
        scale (float): Scale of the image
        maxcolseps (int): Maximum number of whitespace column separators
        black_colseps (bool): Whether column separators are assumed to be
                              vertical black lines or not
        no_hlines (bool): Switch for horizontal line removal
        reading_order_fn (Callable): Function to call to order line output.
                                     Callable accepting a list of slices (y, x)
                                     and a text direction in (`rl`, `lr`).

    Returns:
        {'text_direction': '$dir', 'boxes': [(x1, y1, x2, y2),...]}: A
        dictionary containing the text direction and a list of reading order
        sorted bounding boxes under the key 'boxes'.

    Raises:
        KrakenInputException if the input image is not binarized or the text
        direction is invalid.
    """

    print("SEG A")
    binary = np.array(raw > 0.5 * (np.amin(raw) + np.amax(raw)), "i")
    binary = 1 - binary

    if not scale:
        scale = estimate_scale(binary)

    if no_hlines:
        binary = remove_hlines(binary, scale)
    # emptyish images wll cause exceptions here.

    try:
        if black_colseps:
            colseps, binary = compute_black_colseps(binary, scale, maxcolseps)
        else:
            colseps = compute_white_colseps(binary, scale, maxcolseps)
    except ValueError:

        # Exception in column finder (probably empty image)
        return {"text_direction": text_direction, "boxes": []}

    print("SEG B")
    bottom, top, boxmap = compute_gradmaps(binary, scale)
    seeds = compute_line_seeds(binary, bottom, top, colseps, scale)
    llabels = morph.propagate_labels(boxmap, seeds, conflict=0)
    spread = morph.spread_labels(seeds, maxdist=scale)
    llabels = np.where(llabels > 0, llabels, spread * binary)
    segmentation = llabels * binary

    print("SEG C")
    lines = compute_lines(segmentation, scale)
    order = reading_order_fn([ln.bounds for ln in lines], text_direction[-2:])
    print("SEG D")
    lsort = topsort(order)
    lines = [lines[i].bounds for i in lsort]
    lines = [(s2.start, s1.start, s2.stop, s1.stop) for s1, s2 in lines]

    (maxH, maxW) = raw.shape[0:2]
    print("SEG E")
    lines = [
        (max(x[0], 0), x[1], min(x[2], maxW), x[3])
        for x in lines
    ]
    print("SEG F")

    return {
        "text_direction": text_direction,
        "boxes": lines,
        "script_detection": False,
    }
