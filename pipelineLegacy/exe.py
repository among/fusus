import os
import cv2

from tf.core.timestamp import Timestamp

from .parameters import Config
from .lib import showarray
from .image import ReadableImage


class Exe:
    def __init__(self, **parameters):
        self.config = Config(**parameters)
        self.loadDivisor()
        self.marks = {}
        self.tm = Timestamp()

    def reconfigure(self, reset=False, **parameters):
        """Override configuration settings.

        Configuration settings can be selectively modified.

        !!! caution "Mark loading"
            Mark images may have been loaded, based on the
            previous settings. If the new settings invalidate
            those marks, the loaded marks will be cleared.
            Because of dynamic loading of marks, they will
            be reloaded when needed.

        Parameters
        ----------
        reset: boolean, optional `False`
            Whether to reset the config settings to their default values
            before merging in the new parameters.
        parameters: key=value pairs
            The keys are settings, the values are new values for those settings.
            If a key is not a known setting, a warning will be generated and the
            key will be ignored. If the value is a dictionary, the value
            will be recursively merged into the existing value.
        """

        C = self.config
        C.reconfigure(reset=reset, **parameters)
        if set(parameters) & C.reloadMarks:
            self.marks = {}

    def loadDivisor(self):
        """Load the mark that indicates the division between text and footnotes.
        """

        C = self.config

        markPath = f"{C.MARK_DIR}/{C.DIVISOR}.jpg"
        mark = cv2.imread(markPath)
        mark = cv2.cvtColor(mark, cv2.COLOR_BGR2GRAY)
        self.divisor = mark

    def loadMark(self, markName, acc, bw):
        """Load a single mark.

        Used for loading marks on demand.

        Marks specify their own accuracy, border width and band.
        You can override accuracy and border width.
        """

        tm = self.tm
        warning = tm.error
        C = self.config
        marks = self.marks

        if markName not in self.marks:
            if markName not in C.MARK_INSTRUCTIONS:
                warning(f'Mark "{markName}" not declared')

            markPath = f"{C.MARK_DIR}/{markName}.jpg"
            if not os.path.exists(markPath):
                warning(f'Mark "{markName}" not found')
                return

            mark = cv2.imread(markPath)
            mark = cv2.cvtColor(mark, cv2.COLOR_BGR2GRAY)
            marks[markName] = dict(image=mark)
        else:
            mark = marks[markName]["image"]

        markInfo = marks[markName]
        if bw is None:
            bw = C.MARK_INSTRUCTIONS.get(markName, {}).get("bw", C.BORDER_WIDTH)
        if bw <= 0:
            warning(f"border width of {markName}: changed {bw} to 1")
            bw = 1

        if acc is None:
            acc = C.MARK_INSTRUCTIONS.get(markName, {}).get("acc", C.ACCURACY)

        band = C.MARK_INSTRUCTIONS.get(markName, {}).get("band", C.BAND)

        markInfo["bw"] = bw
        markInfo["acc"] = acc
        markInfo["band"] = band

    def loadMarks(self):
        """Load all known marks.

        Used for loading marks before batch processing of many images.
        """

        tm = self.tm
        warning = tm.error
        C = self.config
        marks = self.marks

        for (markName, markParams) in C.MARK_INSTRUCTIONS.items():
            markPath = f"{C.MARK_DIR}/{markName}.jpg"
            if not os.path.exists(markPath):
                warning(f'Mark "{markName}" not found')
                continue

            mark = cv2.imread(markPath)
            mark = cv2.cvtColor(mark, cv2.COLOR_BGR2GRAY)
            bw = markParams.get("bw", C.BORDER_WIDTH)
            if bw <= 0:
                warning(f"border width of {markName}: changed {bw} to 1")
                bw = 1
            acc = markParams.get("acc", C.ACCURACY)
            band = markParams.get("band", C.BAND)
            marks[markName] = dict(image=mark, band=band, bw=bw, acc=acc)

    def definedMarks(self):
        """Return the currently declared mark instructions.
        """

        C = self.config
        return C.MARK_INSTRUCTIONS

    def start(self, name, ext="jpg"):
        """Initialize an image for processing.

        Parameters
        ----------
        name: string
            The file name of the image (without extension, without directory)
        ext: string, optional `jpg`
            The extension of the file name of the image.

        Returns
        -------
        A readable image object, which is the handle for applying
        further operations.
        """

        return ReadableImage(self, name, ext=ext)

    def testClean(self, name, ext="jpg", **kwargs):
        rImg = ReadableImage(self, name, ext=ext)
        rImg.clean(**kwargs)
        rImg.show(stage="boxed")
        return rImg

    def process(self, name, ext="jpg", batch=False, boxed=True, quiet=False):
        """Process a single image.

        Executes all processing steps for a single image.

        Parameters
        ----------
        name: string
            The file name of the image (without extension, without directory)
        ext: string, optional `jpg`
            The extension of the file name of the image.
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
        if not batch:
            info(f"Processing {name}")

        rImg = ReadableImage(self, name, ext=ext, batch=batch, boxed=boxed)
        if batch or not rImg.empty:
            if not batch:
                indent(level=subLevel, reset=True)
                info("normalizing")
            rImg.normalize()
            if not batch:
                info("histogram")
            rImg.histogram()
            if not batch:
                info("margins")
            rImg.margins()
            if not batch:
                info("cleaning")
            rImg.clean()

        tm.silentOff()

        if not batch:
            indent(level=baseLevel)
            div = rImg.divisor
            info(f"Done, kept {div[2]:>3}% of the page")
            if not quiet:
                divIm = div[1]
                if divIm is not None:
                    showarray(divIm)
        return rImg

    def batch(self, ext="jpg", quiet=True, boxed=False):
        """Process a directory of images.

        Executes all processing steps for all images.

        Parameters
        ----------
        ext: string, optional `jpg`
            The extension of the file names of the images.
        boxed: boolean, optional `False`
            If in batch mode, produce also images that display the cleaned marks
            in boxes.
        quiet: boolean, optional `True`
            Whether to suppress warnings and the display of footnote separators.
        """

        C = self.config
        tm = self.tm
        info = tm.info
        error = tm.error
        indent = tm.indent
        tm.silentOff()

        indent(reset=True)

        inDir = C.PREOCR_INPUT
        theExt = None if not ext else f".{ext}"

        if not os.path.exists(inDir):
            error("PreOCR input directory not found: {inDir}")
            return False

        imageFiles = []
        with os.scandir(inDir) as it:
            for entry in it:
                name = entry.name
                if (
                    not name.startswith(".")
                    and entry.is_file()
                    and (theExt is None or name.endswith(theExt))
                ):
                    imageFiles.append(name)

        info(f"Batch of {len(imageFiles)} pages in {inDir}")
        info(f"Loading marks for cleaning")

        self.loadMarks()

        info(f"Start batch processing images")
        for (i, imFile) in enumerate(sorted(imageFiles)):
            indent(level=1, reset=True)
            msg = f"{i + 1:>5} {imFile:<40}"
            info(f"{msg}\r", nl=False)
            rImg = self.process(
                imFile[0:-4], ext="jpg", batch=True, boxed=boxed, quiet=quiet
            )
            rImg.write(stage="clean")
            if boxed:
                rImg.write(stage="boxed")
            div = rImg.divisor
            info(f"{msg} {div[2]:>3}%")
            if not quiet:
                divIm = div[1]
                if divIm is not None:
                    showarray(divIm)
        indent(level=0)
        info("all done")


def main():
    EX = Exe()
    rImg = EX.treatImage("qay_Page_1")
    answer = input("show result image? [Y] ")
    if answer == "Y":
        rImg.show(stage="clean")


if __name__ == "__main__":
    main()
