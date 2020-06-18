from pytesseract import image_to_data, image_to_string, image_to_boxes


MODES = dict(
    string=image_to_string,
    data=image_to_data,
    boxes=image_to_boxes,
)


class OCR:
    def __init__(self, engine, page=None, pageFile=None):
        """Sets up OCR with Tesseract.
        """

        tm = engine.tm
        error = tm.error

        batch = None
        if page is None and pageFile is None:
            error("Pass a page object or a page file with a list of file names")
        elif page:
            batch = False
            self.page = page
        elif pageFile:
            batch = True
            self.pageFile = pageFile

        self.batch = batch
        self.engine = engine

    def read(self, mode=None):
        """Perfroms OCR with Tesseract.
        """

        engine = self.engine
        tm = engine.tm
        error = tm.error
        batch = self.batch

        if batch is None:
            error("No input to work on")
            return None

        if not mode:
            mode = 'data'

        method = MODES.get(mode, None)
        if method is None:
            error(f"No such read mode: {mode}")

        if batch:
            ocrData = method(self.pageFile, lang="ara")
        else:
            scan = self.page.stages.get("clean", None)
            if scan is None:
                return None

            ocrData = method(scan, lang="ara")

        return ocrData
