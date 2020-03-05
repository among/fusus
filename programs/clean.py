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

    def loadElement(self, elemName, bw):
        if elemName in self.elements and bw in self.elements[elemName]:
            return

        C = self.config

        if elemName not in C.ELEMENT_INSTRUCTIONS:
            sys.stderr.write(f'Element "{elemName}" not declared')

        elemPath = f"{C.ELEMENT_DIR}/{elemName}.jpg"
        elem = cv2.imread(elemPath)
        elem = cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
        if bw is None:
            bw = C.BORDER_WIDTH
        if bw:
            elem = cv2.copyMakeBorder(
                elem, bw, bw, bw, bw, cv2.BORDER_CONSTANT, value=C.WHITE
            )
        self.elements.setdefault(elemName, {})[bw] = elem

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

    def process(self, name, ext="jpg"):
        pImg = ProcessedImage(self, name, ext=ext)
        pImg.normalize()
        pImg.histogram()
        pImg.margins()
        pImg.clean()
        return pImg


def main():
    CL = CleanupEngine()
    pImg = CL.treatImage("qay_Page_1")
    answer = input("show result image? [Y] ")
    if answer == "Y":
        pImg.show(stage="clean")


if __name__ == "__main__":
    main()
