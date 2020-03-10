import os
import sys
import cv2

from parameters import Config

from image import ProcessedImage


class CleanupEngine:
    def __init__(self, **parameters):
        self.config = Config(parameters)
        self.loadDivisor()
        self.elements = {}

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
        C = self.config
        elements = self.elements

        if elemName not in self.elements:
            if elemName not in C.ELEMENT_INSTRUCTIONS:
                sys.stderr.write(f'Element "{elemName}" not declared\n')

            elemPath = f"{C.ELEMENT_DIR}/{elemName}.jpg"
            if not os.path.exists(elemPath):
                sys.stderr.write(f'Element "{elemName}" not found\n')
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
            sys.stderr.write(f"border width of {elemName}: changed {bw} to 1\n")
            bw = 1

        if acc is None:
            acc = C.ELEMENT_INSTRUCTIONS.get(elemName, {}).get("acc", C.ACCURACY)

        elemInfo["bw"] = bw
        elemInfo["acc"] = acc

    def loadElements(self):
        C = self.config
        elements = self.elements

        for (elemName, elemParams) in C.ELEMENT_INSTRUCTIONS.items():
            elemPath = f"{C.ELEMENT_DIR}/{elemName}.jpg"
            if not os.path.exists(elemPath):
                sys.stderr.write(f'Element "{elemName}" not found\n')
                continue

            elem = cv2.imread(elemPath)
            elem = cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
            bw = elemParams.get("bw", C.BORDER_WIDTH)
            if bw <= 0:
                sys.stderr.write(f"border width of {elemName}: changed {bw} to 1\n")
                bw = 1
            acc = elemParams.get("acc", C.ACCURACY)
            elements[elemName] = dict(image=elem, bw=bw, acc=acc)

    def definedElements(self):
        C = self.config
        return C.ELEMENT_INSTRUCTIONS

    def start(self, name, ext="jpg"):
        return ProcessedImage(self, name, ext=ext)

    def testClean(self, name, ext="jpg", **kwargs):
        pImg = ProcessedImage(self, name, ext=ext)
        pImg.clean(**kwargs)
        pImg.show(stage="boxed")
        return pImg

    def process(self, name, ext="jpg", batch=False):
        pImg = ProcessedImage(self, name, ext=ext, batch=batch)
        if batch or not pImg.empty:
            pImg.normalize()
            pImg.histogram()
            pImg.margins()
            pImg.clean()
        return pImg

    def batch(self, ext="jpg"):
        C = self.config
        inDir = C.PREOCR_INPUT
        theExt = None if not ext else f".{ext}"

        if not os.path.exists(inDir):
            sys.stderr.write("PreOCR input directory not found: {inDir}\n")
            return False

        self.loadElements()

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
        sys.stdout.write(f"Batch of {len(imageFiles)} pages in {inDir} :\n")
        for (i, imFile) in enumerate(sorted(imageFiles)):
            sys.stdout.write(f"\r\t{i + 1:>5} {imFile:<40}  ...")
            pImg = self.process(imFile[0:-4], ext="jpg", batch=True)
            pImg.write(stage="clean")
        sys.stdout.write(f"\r\t{i + 1:>5} {imFile:<40}  Done")


def main():
    CL = CleanupEngine()
    pImg = CL.treatImage("qay_Page_1")
    answer = input("show result image? [Y] ")
    if answer == "Y":
        pImg.show(stage="clean")


if __name__ == "__main__":
    main()
