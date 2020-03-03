import io
import cv2
import numpy as np
import PIL.Image
from IPython.display import Image, display


def showarray(a, fmt='jpeg', **kwargs):
    a = np.uint8(np.clip(a, 0, 255))
    f = io.BytesIO()
    PIL.Image.fromarray(a).save(f, fmt)
    display(Image(data=f.getvalue(), **kwargs))


class ProcessedImage:
    def __init__(self, folder, name, ext='jpg'):
        self.folder = folder
        self.name = name
        self.ext = ext
        path = f"{folder}/{name}.{ext}"
        self.img = cv2.imread(path)
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

    def write(self, folder=None, name=None, ext=None):
        if folder is None:
            folder = self.folder
        if name is None:
            name = self.name
        if ext is None:
            ext = self.ext
        path = f"{folder}/{name}.{ext}"
        cv2.imwrite(path, self.img)

    def showCV(self, label=None):
        if label is None:
            label = self.name
        cv2.imshow(label, self.img)
        cv2.waitKey(0)
        cv2.destroyWindows(label)

    def show(self, **kwargs):
        showarray(self.img, **kwargs)
