import os
import sys
import cv2

from glob import glob

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

    def batch(self, name, ext="jpg"):
        C = self.config

        if not os.path.exists(C.PREOCR_INPUT):
            sys.stderr.write("PreOCR input directory not found: {C.PREOCR_INPUT}\n")
            return False

        self.loadElements()

        for imFile in sorted(glob(f"{C.PREOCR_INPUT}/*.jpg")):
            pImg = self.process(imFile[0:-4], ext="jpg", batch=True)
            pImg.write(stage="clean")


def main():
    CL = CleanupEngine()
    pImg = CL.treatImage("qay_Page_1")
    answer = input("show result image? [Y] ")
    if answer == "Y":
        pImg.show(stage="clean")


if __name__ == "__main__":
    main()
