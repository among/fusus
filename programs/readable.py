import os
import cv2

from tf.core.timestamp import Timestamp
from parameters import Config

from lib import showarray
from image import ReadableImage


class Readable:
    def __init__(self, **parameters):
        self.config = Config(parameters)
        self.loadDivisor()
        self.elements = {}
        self.tm = Timestamp()

    def reconfigure(self, **parameters):
        C = self.config
        C.reconfigure(**parameters)
        if set(parameters) & C.reloadElements:
            self.elements = {}

    def loadDivisor(self):
        C = self.config

        elemPath = f"{C.ELEMENT_DIR}/{C.DIVISOR}.jpg"
        elem = cv2.imread(elemPath)
        elem = cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
        self.divisor = elem

    def loadElement(self, elemName, acc, bw):
        tm = self.tm
        warning = tm.error
        C = self.config
        elements = self.elements

        if elemName not in self.elements:
            if elemName not in C.ELEMENT_INSTRUCTIONS:
                warning(f'Element "{elemName}" not declared')

            elemPath = f"{C.ELEMENT_DIR}/{elemName}.jpg"
            if not os.path.exists(elemPath):
                warning(f'Element "{elemName}" not found')
                return

            elem = cv2.imread(elemPath)
            elem = cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
            elements[elemName] = dict(image=elem)
        else:
            elem = elements[elemName]["image"]

        elemInfo = elements[elemName]
        if bw is None:
            bw = C.ELEMENT_INSTRUCTIONS.get(elemName, {}).get("bw", C.BORDER_WIDTH)
        if bw <= 0:
            warning(f"border width of {elemName}: changed {bw} to 1")
            bw = 1

        if acc is None:
            acc = C.ELEMENT_INSTRUCTIONS.get(elemName, {}).get("acc", C.ACCURACY)

        band = C.ELEMENT_INSTRUCTIONS.get(elemName, {}).get("band", C.BAND)

        elemInfo["bw"] = bw
        elemInfo["acc"] = acc
        elemInfo["band"] = band

    def loadElements(self):
        tm = self.tm
        warning = tm.error
        C = self.config
        elements = self.elements

        for (elemName, elemParams) in C.ELEMENT_INSTRUCTIONS.items():
            elemPath = f"{C.ELEMENT_DIR}/{elemName}.jpg"
            if not os.path.exists(elemPath):
                warning(f'Element "{elemName}" not found')
                continue

            elem = cv2.imread(elemPath)
            elem = cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
            bw = elemParams.get("bw", C.BORDER_WIDTH)
            if bw <= 0:
                warning(f"border width of {elemName}: changed {bw} to 1")
                bw = 1
            acc = elemParams.get("acc", C.ACCURACY)
            band = elemParams.get("band", C.BAND)
            elements[elemName] = dict(image=elem, band=band, bw=bw, acc=acc)

    def definedElements(self):
        C = self.config
        return C.ELEMENT_INSTRUCTIONS

    def start(self, name, ext="jpg"):
        return ReadableImage(self, name, ext=ext)

    def testClean(self, name, ext="jpg", **kwargs):
        rImg = ReadableImage(self, name, ext=ext)
        rImg.clean(**kwargs)
        rImg.show(stage="boxed")
        return rImg

    def process(self, name, ext="jpg", batch=False, boxed=True, quiet=False):
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

        self.loadElements()

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
    RB = Readable()
    rImg = RB.treatImage("qay_Page_1")
    answer = input("show result image? [Y] ")
    if answer == "Y":
        rImg.show(stage="clean")


if __name__ == "__main__":
    main()
