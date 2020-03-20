import sys
import os

import yaml
import cv2

from tf.core.timestamp import Timestamp

from .lib import showImage, imageFileList, select, splitext, configure
from .image import ReadableImage

DEFAULTS = dict(
    inDir="in",
    outDir="out",
    interDir="inter",
    marks="marks",
    dividers="dividers",
    accuracy=0.8,
    connectBorder=4,
    band="inter",
)


class Book:
    def __init__(self, **params):
        C = configure(DEFAULTS, params)
        self.C = C
        self.tm = Timestamp()

        params = ("accuracy", "connectBorder", "band")
        infoFile = "marks.yaml"

        self.dividers = {}
        self.marks = {}

        if os.path.exists(infoFile):
            with open(infoFile) as fh:
                markInfo = yaml.load(fh, Loader=yaml.FullLoader)
        else:
            markInfo = {}

        for (path, dest) in (
            (C["dividers"], self.dividers),
            (C["marks"], self.marks),
        ):
            files = imageFileList(path)
            for f in files:
                (bare, ext) = splitext(f)
                full = f"{path}/{f}"
                image = cv2.imread(full)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                dest[bare] = dict(gray=gray)
                for k in params:
                    dest[bare][k] = markInfo.get(bare, {}).get(k, DEFAULTS[k])

    def start(self, f):
        """Initialize an image for processing.

        Parameters
        ----------
        f: string
            The file name of the image with extension, without directory

        Returns
        -------
        A readable image object, which is the handle for applying
        further operations.
        """

        return ReadableImage(self, f)

    def process(
        self,
        f,
        batch=False,
        boxed=True,
        quiet=False,
        normalize=None,
        margins=None,
        clean=None,
    ):
        """Process a single image.

        Executes all processing steps for a single image.

        Parameters
        ----------
        f: string
            The file name of the image with extension, without directory
        batch: boolean, optional `False`
            Whether to run in batch mode.
            In batch mode everything is geared to the final output.
            Less intermediate results are computed and stored.
            Less feedback happens on the console.
        boxed: boolean, optional `True`
            If in batch mode, produce also images that display the cleaned marks
            in boxes.
        quiet: boolean, optional `False`
            Whether to suppress warnings and the display of footnote separators.

        Returns
        -------
        A readable image object, which is the handle for further
        inspection of what has happened during processing.
        """

        tm = self.tm
        info = tm.info
        indent = tm.indent
        if quiet:
            tm.silentOn(deep=True)
        else:
            tm.silentOff()

        baseLevel = 1 if batch else 0
        subLevel = baseLevel + 1
        indent(level=baseLevel, reset=True)

        (bare, ext) = splitext(f)

        if not batch:
            info(f"Processing {bare}")

        rImg = ReadableImage(self, f, batch=batch, boxed=boxed)
        if batch or not rImg.empty:
            if not batch:
                indent(level=subLevel, reset=True)
                info("normalizing")
            rImg.normalize(**(normalize or {}))
            if not batch:
                info("histogram")
            rImg.histogram()
            if not batch:
                info("margins")
            rImg.margins(**(margins or {}))
            if not batch:
                info("cleaning")
            rImg.clean(**(clean or {}))

        tm.silentOff()

        if not batch:
            indent(level=baseLevel)
            div = rImg.dividers.get("footnote", None)
            if div:
                msg = "footer"
                amount = f"at height {div[2]:>3}%"
            else:
                msg = "no footer"
                amount = ""
            info(f"Done, {msg} {amount}")
            if not quiet:
                divIm = div[1]
                if divIm is not None:
                    showImage(divIm)
        return rImg

    def batch(
        self,
        pages=None,
        batch=True,
        quiet=True,
        boxed=False,
        normalize=None,
        margins=None,
        clean=None,
    ):
        """Process directory of images.

        Executes all processing steps for all images.

        Parameters
        ----------
        pages: string | int, optional `None`
            Specification of pages to do. If absent or `None`: all pages.
            If an int, do only that page.
            Otherwise it must be a comma separated string of (ranges of) page numbers.
            Half ranges are also allowed: `-10` (from beginning up to and including `10`)
            and `10-` (from 10 till end).
            E.g. `1` and `5-7` and `2-5,8-10`, and `-10,15-20,30-`.
            No spaces allowed.
        boxed: boolean, optional `False`
            If in batch mode, produce also images that display the cleaned marks
            in boxes.
        quiet: boolean, optional `True`
            Whether to suppress warnings and the display of footnote separators.
        """

        tm = self.tm
        info = tm.info
        indent = tm.indent
        tm.silentOff()

        indent(reset=True)

        C = self.C
        inDir = C["inDir"]
        interDir = C["interDir"]
        outDir = C["outDir"]
        for d in (interDir, outDir):
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)

        imageFiles = select(imageFileList(inDir), pages)
        info(f"Batch of {len(imageFiles)} pages")

        info(f"Start batch processing images")
        for (i, imFile) in enumerate(sorted(imageFiles)):
            indent(level=1, reset=True)
            msg = f"{i + 1:>5} {imFile:<40}"
            info(f"{msg}\r", nl=False)
            rImg = self.process(
                imFile,
                batch=batch,
                boxed=boxed,
                quiet=quiet,
                normalize=normalize,
                margins=margins,
                clean=clean,
            )
            rImg.write(stage="clean")
            if boxed:
                rImg.write(stage="boxed")
            div = rImg.dividers.get("footnote", None)
            amount = div[2] if div else 100
            info(f"{msg} {amount:>3}%")
            if not quiet:
                divIm = div[1]
                if divIm is not None:
                    showImage(divIm)
        indent(level=0)
        info("all done")
        return rImg  # the last image processed


def main():
    pages = None
    if len(sys.argv) > 1:
        pages = sys.argv[1]
    EX = Book()
    EX.batch(pages=pages)


if __name__ == "__main__":
    main()
