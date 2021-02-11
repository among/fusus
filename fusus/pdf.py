import os
import fitz

from .lib import DEFAULT_EXTENSION


"""Installation

```
pip3 install PyMuPDF
```

See [docs](https://pymupdf.readthedocs.io/en/latest/index.html)
"""


def pdf2png(inPdf, outDir, silent=True):
    """Extract all images in a PDF to an output directory.
    """

    doc = fitz.open(inPdf)
    if not os.path.exists(outDir):
        os.makedirs(outDir, exist_ok=True)

    p = 0
    for i in range(len(doc)):
        imgList = doc.getPageImageList(i)
        for entry in imgList:
            p += 1
            xref = entry[0]
            pix = fitz.Pixmap(doc, xref)
            pix.writeImage(f"{outDir}/{p:>03}.{DEFAULT_EXTENSION}")
    if not silent:
        plural = "" if p == 1 else "s"
        print(f"Written {p} image{plural}")
