import cv2
import numpy as np

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

COLOR = {
    False: (255, 0, 255),
    True: (255, 255, 255),
}

BORDER = {
    False: 3,
    True: -1,
}


class CleanupEngine:
    def __init__(self, elementDir):
        self.elementDir = elementDir
        self.loadElements()

    def loadElements(self):
        self.elements = []
        for (elem, acc) in ELEMENT_INSTRUCTIONS:
            elemPath = f"{self.elementDir}/{elem}.jpg"
            elem = cv2.imread(elemPath)
            self.elements.append((cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY), acc))

    def useElements(self, img, gray, color, border):
        for (elem, acc) in self.elements:
            (H, W) = elem.shape[:2]
            result = cv2.matchTemplate(gray, elem, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= acc)
            for pt in zip(*loc[::-1]):
                cv2.rectangle(img, pt, (pt[0] + W, pt[1] + H), color, border)
                cv2.rectangle(gray, pt, (pt[0] + W, pt[1] + H), color, border)

    def treatImage(self, folderIn, folderOut, name, ext='jpg', destroy=True):
        color = COLOR[destroy]
        border = BORDER[destroy]
        showRep = '' if destroy else '-find'

        pImg = ProcessedImage(folderIn, name, ext=ext)
        self.useElements(pImg.img, pImg.gray, color, border)
        pImg.write(folder=folderOut, name=f"{name}{showRep}")
        return (pImg, showRep)


def main():
    CL = CleanupEngine(ELEMENT_DIR)
    (pImg, showRep) = CL.treatImage(PREOCR_INPUT, OCR_INPUT, 'qay_Page_1', destroy=False)
    answer = input("show result image? [Y] ")
    if answer == 'Y':
        pImg.show()


if __name__ == "__main__":
    main()
