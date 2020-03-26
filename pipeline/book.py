"""Book pipeline
"""

import sys
import os

import cv2

from tf.core.timestamp import Timestamp

from .parameters import Config
from .lib import (
    showImage,
    imageFileList,
    imageFileListSub,
    select,
    splitext,
    pagesRep,
    tempFile,
)
from .page import Page
from .ocr import OCR


class Book:
    def __init__(self, **params):
        """Engine for book conversion.

        Parameters
        ----------
        params: dict, optional
            Any number of customizable settings from `pipeline.parameters.SETTINGS`.

            They will be in effect when running the pipeline, until
            a `Book.configure` action will modify them.
        """

        tm = Timestamp()
        self.tm = tm
        self.C = Config(tm, **params)
        self._applySettings()

    def _applySettings(self):
        """After a settings update, recompute derived settings.
        """

        C = self.C
        tm = self.tm
        error = tm.error

        markParams = dict(acc="accuracy", cb="connectBorder")

        self.marks = {}
        marks = self.marks
        self.dividers = {}
        dividers = self.dividers
        offsetBand = {band: offset for (band, offset) in C.offsetBand.items()}
        self.offsetBand = offsetBand

        files = imageFileListSub(C.marksDir)

        seq = 0

        for (band, images) in files.items():
            for f in images:
                tweakDict = {}
                bare = splitext(f)[0]
                parts = bare.rsplit("(", 1)
                if len(parts) > 1:
                    bare = parts[0]
                    tweaks = parts[1][0:-1].split(",")
                    for tweak in tweaks:
                        if "=" not in tweak:
                            error(f"Malformed image parameter for {bare}: {tweak}")
                            continue
                        (k, v) = tweak.split("=", 1)
                        if k not in markParams:
                            error(f"Unknown image parameter for {bare}: {k} in {k}={v}")
                            continue
                        try:
                            tweakDict[k] = int(v) if k == "cb" else float(v)
                        except Exception:
                            error(f"Unknown image parameter for {bare}: {v} in {k}={v}")

                full = f"{C.marksDir}/{band}/{f}"
                image = cv2.imread(full)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                if band == "divider":
                    dividers[bare] = dict(gray=gray)
                    dest = dividers[bare]
                else:
                    seq += 1
                    marks.setdefault(band, {})[bare] = dict(gray=gray, seq=seq)
                    dest = marks[band][bare]
                for (k, kLong) in markParams.items():
                    dest[kLong] = tweakDict.get(k, getattr(C, kLong))

        self.allPages = imageFileList(C.inDir)
        self.allPagesDesc = pagesRep(self.allPages)

    def configure(self, reset=False, **params):
        """Updates current settings based on new values.

        The signature is the same as `pipeline.parameters.Config.configure`.
        """

        self.C.configure(reset=reset, **params)
        self._applySettings()

    def showSettings(self, params=None):
        """Display settings.

        Parameters
        ----------
        params: dict, optional
            Any number of customizable settings from `pipeline.parameters.SETTINGS`.

            The current values of given parameters will be displayed.
            The values that you give each of the `params` here is not used,
            only their names. It is recommended to pass `None` as values:

            `B.showSettings(blurX=None, blurY=None)`
        """
        self.C.show(params=params)

    def availableBands(self):
        """Display the characteristics of all defined *bands*.
        """

        tm = self.tm
        info = tm.info

        info("Available bands and their offsets", tm=False)
        for (band, offset) in sorted(self.offsetBand.items()):
            bandRep = f"«{band}»"
            info(
                f"\t{bandRep:<10}: top={offset[0]:>4}, bottom={offset[1]:>4}", tm=False
            )

    def availableMarks(self):
        """Display the characteristics of all defined *marks*.
        """

        tm = self.tm
        info = tm.info
        marks = self.marks

        info("Marks and their settings", tm=False)
        for (band, markItems) in sorted(marks.items()):
            bandRep = f"[{band}]"
            info(f"\tband {bandRep}", tm=False)
            for (mark, markInfo) in sorted(markItems.items()):
                markRep = f"«{mark}»"
                seq = markInfo["seq"]
                acc = markInfo["accuracy"]
                cb = markInfo["connectBorder"]
                info(
                    f"\t\t{seq:>3}: {markRep:<20} accuracy={acc}, connectBorder={cb}",
                    tm=False,
                )
                showImage(markInfo["gray"])

    def availablePages(self):
        """Display the amount and page numbers of all pages.
        """

        tm = self.tm
        info = tm.info

        allPages = self.allPages
        pagesDesc = self.allPagesDesc

        info(f"{len(allPages)} pages: {pagesDesc}")

    def _doPage(
        self, f, batch=False, boxed=True, quiet=False, doOcr=True,
    ):
        """Process a single page.

        Executes all processing steps for a single page.

        Parameters
        ----------
        f: string
            The file name of the scanned page with extension, without directory
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
        doOcr: boolean, optional `True`
            Whether to perform OCR processing

        Returns
        -------
        A `pipeline.page.Page` object, which is the handle for further
        inspection of what has happened during processing.
        """

        tm = self.tm
        info = tm.info
        indent = tm.indent
        if quiet:
            tm.silentOn(deep=True)
        else:
            tm.silentOff()

        # baseLevel = 1 if batch else 0
        baseLevel = 1
        subLevel = baseLevel + 1
        indent(level=baseLevel, reset=True)

        bare = splitext(f)[0]

        if not batch:
            info(f"Processing {bare}")

        page = Page(self, f, batch=batch, boxed=boxed)
        if batch or not page.empty:
            if not batch:
                indent(level=subLevel, reset=True)
                info("normalizing")
            page.normalize()
            if not batch:
                info("histogram")
            page.histogram()
            if not batch:
                info("margins")
            page.margins()
            if not batch:
                info("cleaning")
            page.clean()
            if not batch:
                if doOcr:
                    info("ocr")
                    page.ocr()

        tm.silentOff()

        return page

    def process(
        self, pages=None, batch=True, quiet=True, boxed=False, doOcr=True,
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
        batch: boolean, optional `True`
            Whether to run in batch mode.
            In batch mode everything is geared to the final output.
            Less intermediate results are computed and stored.
            Less feedback happens on the console.
        boxed: boolean, optional `False`
            If in batch mode, produce also images that display the cleaned marks
            in boxes.
        quiet: boolean, optional `True`
            Whether to suppress warnings and the display of footnote separators.
        doOcr: boolean, optional `True`
            Whether to perform OCR processing

        Returns
        -------
        A `pipeline.page.Page` object for the last page processed,
        which is the handle for further
        inspection of what has happened during processing.
        """

        tm = self.tm
        info = tm.info
        indent = tm.indent

        allPages = self.allPages

        tm.silentOff()

        indent(reset=True)

        C = self.C
        interDir = C.interDir
        outDir = C.outDir
        for d in (interDir, outDir):
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)

        imageFiles = select(allPages, pages)
        pagesDesc = pagesRep(imageFiles)
        info(f"Batch of {len(imageFiles)} pages: {pagesDesc}")

        info(f"Start batch processing images")
        for (i, imFile) in enumerate(sorted(imageFiles)):
            indent(level=1, reset=True)
            msg = f"{i + 1:>5} {imFile:<40}"
            info(f"{msg}\r", nl=False)
            page = self._doPage(
                imFile, batch=batch, boxed=boxed, quiet=quiet, doOcr=doOcr
            )
            page.write(stage="clean")
            if not batch:
                page.write(stage="data")
            if boxed:
                page.write(stage="boxed")
            div = page.dividers.get("footnote", None)
            amount = div[2] if div else 100
            info(f"{msg} {amount:>3}%")
            if not quiet:
                divIm = div[1]
                if divIm is not None:
                    showImage(divIm)
        indent(level=0)
        info("all done")

        if doOcr and batch:
            indent(level=1, reset=True)
            info(f"Start batch OCR of all clean images")

            with tempFile() as tmp:
                for pg in imageFiles:
                    (bare, ext) = splitext(pg)
                    pgClean = f"{bare}-clean{ext}"
                    tmp.write(f"{interDir}/{pgClean}\n")
                tmp.flush()
                name = tmp.name
                reader = OCR(self, pageFile=name)
                data = reader.read()
                dataFile = f"{outDir}/data{'' if pages is None else pagesDesc}.tsv"
                if data is not None:
                    with open(dataFile, "w") as df:
                        df.write(data)

            info("OCR done")
            indent(level=0)
        info("all done")

        return page  # the last page processed


def main():
    """Process a whole book with default settings.

    Go to the book directory and say

    ```
    python3 -m pipeline.book [pages]
    ```

    where `pages` is an optional string specifying ranges
    of pages as in `Book.process`
    """

    pages = None
    if len(sys.argv) > 1:
        pages = sys.argv[1]
    B = Book()
    B.process(pages=pages)


if __name__ == "__main__":
    main()
