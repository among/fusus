import cv2

from parameters import ELEMENT_DIR, PREOCR_INPUT, OCR_INPUT
from image import ProcessedImage


ELEMENT_INSTRUCTIONS = (
    ("shadda", 0.8),
    ("shadda2", 0.8),
    ("shadda3", 0.8),
    ("semicolon", 0.8),
    ("colon", 0.8),
    ("period", 0.9),
    ("comma", 0.6),
    ("tanwin", 0.7),
    ("tanwin2", 0.7),
    ("longA", 0.8),
    ("doubleOpen", 0.7),
    ("doubleClose", 0.7),
    ("salla", 0.75),
    ("alayh", 0.65),
)

DIVISOR = "division"

WHITE = [255, 255, 255]
BORDER_WIDTH = 0


class CleanupEngine:
    def __init__(self, elementDir):
        self.elementDir = elementDir
        self.loadDivisor()
        self.loadElements()

    def loadDivisor(self):
        elemPath = f"{self.elementDir}/{DIVISOR}.jpg"
        elem = cv2.imread(elemPath)
        elem = cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
        self.divisor = elem

    def loadElements(self):
        self.elements = []
        bw = BORDER_WIDTH
        for (elem, acc) in ELEMENT_INSTRUCTIONS:
            elemPath = f"{self.elementDir}/{elem}.jpg"
            elem = cv2.imread(elemPath)
            elem = cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
            if bw:
                elem = cv2.copyMakeBorder(
                    elem, bw, bw, bw, bw, cv2.BORDER_CONSTANT, value=WHITE
                )
            self.elements.append((elem, acc))

    def treatImage(self, folderIn, folderOut, name, ext="jpg", destroy=True):
        showRep = "" if destroy else "-find"

        pImg = ProcessedImage(folderIn, name, ext=ext)
        pImg.normalize()
        pImg.histogram()
        pImg.margins(self.divisor)
        pImg.clean(self.elements, destroy)

        pImg.write(folder=folderOut, name=f"{name}{showRep}")
        return (pImg, showRep)


def main():
    CL = CleanupEngine(ELEMENT_DIR)
    (pImg, showRep) = CL.treatImage(
        PREOCR_INPUT, OCR_INPUT, "qay_Page_1", destroy=False
    )
    answer = input("show result image? [Y] ")
    if answer == "Y":
        pImg.show(stage=None)


if __name__ == "__main__":
    main()
