import os
from copy import deepcopy
import io
import collections

import numpy as np
import PIL.Image
from IPython.display import HTML, Image, display
import cv2

EXTENSIONS = set("""
    jpeg
    jpg
    png
    tif
    tiff
""".strip().split())


def merge(dest, updates):
    for k, v in updates.items():
        if (
            k in dest
            and isinstance(dest[k], dict)
            and isinstance(updates[k], collections.Mapping)
        ):
            merge(dest[k], updates[k])
        else:
            dest[k] = updates[k]


def configure(defaults, updates):
    if updates:
        C = deepcopy(defaults)
        merge(C, updates)
    else:
        C = defaults
    return C


def img(data):
    return f"""<img src="data:image/jpeg;base64,{data}">"""


def showImage(a, fmt="jpeg", **kwargs):
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


def splitext(f):
    (bare, ext) = os.path.splitext(f)
    if ext:
        ext = ext[1:]
    return (bare, ext)


def imageFileList(imDir):
    if not os.path.exists(imDir):
        return []

    imageFiles = []
    with os.scandir(imDir) as it:
        for entry in it:
            name = entry.name
            (bare, ext) = splitext(name)

            if (
                not name.startswith(".")
                and entry.is_file()
                and ext in EXTENSIONS
            ):
                imageFiles.append(name)
    return sorted(imageFiles)


def select(source, selection):
    if selection is None:
        return sorted(source)

    index = {int(splitext(f)[0].lstrip('0')): f for f in source}
    universe = set(index)
    if type(selection) is int:
        return sorted(index[n] for n in {selection} & universe)

    minu = min(universe, default=0)
    maxu = max(universe, default=0)
    selected = set()
    for rng in selection.split(','):
        parts = rng.split('-')
        if len(parts) == 2:
            (lower, upper) = parts
            lower = minu if lower == '' else int(lower)
            upper = maxu if upper == '' else int(upper)
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


def connected(h, w, bw, threshold, gray, hitPoint):
    (textH, textW) = gray.shape
    (hitY, hitX) = hitPoint

    # print(hitPoint)
    connDegree = 0
    nparts = 0

    # left boundary
    f = max((0, hitX - bw)) if hitX > 0 else None
    if f is not None:
        t = hitX
        texto = np.array(
            (255 - gray[hitY : hitY + h, f:t]).max(axis=1), dtype=np.uint16
        )
        fi = hitX
        ti = hitX + bw
        texti = np.array(
            (255 - gray[hitY : hitY + h, fi:ti]).max(axis=1), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        # showit("l", texto, texti, val)
        connDegree += val
        nparts += 1

    # right boundary
    t = min((textW, hitX + w + bw + 1)) if hitX + w + bw < textW else None
    if t is not None:
        f = hitX + w
        # texto = np.array(gray[hitY : hitY + h, f:t])
        # print(texto)
        texto = np.array(
            (255 - gray[hitY : hitY + h, f:t]).max(axis=1), dtype=np.uint16
        )
        ti = hitX + w
        fi = hitX + w - bw
        texti = np.array(
            (255 - gray[hitY : hitY + h, fi:ti]).max(axis=1), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        # showit("r", texto, texti, val)
        connDegree += val
        nparts += 1

    # top boundary

    f = max((0, hitY - bw)) if hitY > 0 else None
    if f is not None:
        t = hitY
        texto = np.array(
            (255 - gray[f:t, hitX : hitX + w]).max(axis=0), dtype=np.uint16
        )
        fi = hitY
        ti = hitY + bw + 1
        texti = np.array(
            (255 - gray[fi:ti, hitX : hitX + w]).max(axis=0), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        # showit("t", texto, texti, val)
        connDegree += val
        nparts += 1

    # bottom boundary

    t = min((textH - 1, hitY + h + bw + 1)) if hitY + h + bw < textH else None
    if t is not None:
        f = hitY + h
        texto = np.array(
            (255 - gray[f:t, hitX : hitX + w]).max(axis=0), dtype=np.uint16
        )
        ti = hitY + h
        fi = hitY + h - bw
        texti = np.array(
            (255 - gray[fi:ti, hitX : hitX + w]).max(axis=0), dtype=np.uint16
        )
        val = measure(texto, texti, threshold)
        # showit("b", texto, texti, val)
        connDegree += val
        nparts += 1
    # print(f"connectedDegree = {connDegree}\n")
    return connDegree


def removeSkewStripes(img, skewBorder, skewColor):
    (h, w) = img.shape[0:2]
    if min((h, w)) < skewBorder * 10:
        return
    for rect in (
        ((0, 0), (skewBorder, h)),
        ((0, 0), (w, skewBorder)),
        ((w, h), (w - skewBorder, 0)),
        ((w, h), (0, h - skewBorder)),
    ):
        cv2.rectangle(img, *rect, skewColor, -1)
