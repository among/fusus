import sys
import os


class Config:
    config = dict(
        DATA_BASE_DIR=os.path.expanduser("~/Documents"),
        CODE_BASE_DIR=os.path.expanduser("~/github"),
        CODE_ORG="dirkroorda",
        DATA_ORG="annotation",
        PROJECT="fusus",
        STEP_PREOCR="preocr",
        STEP_OCR="ocr",
        ACCURACY=0.8,
        MARGIN_THRESHOLD=5,
        MARGIN_COLOR=(250, 250, 250),
        GRID_UPPER_COLOR=(0, 0, 255),
        GRID_LOWER_COLOR=(0, 255, 0),
        GRID_UPPER_LEEWAY=10,
        GRID_LOWER_LEEWAY=20,
        CLEAN_HIGHLIGHT=((240, 170, 20), (170, 240, 40), 3),
        CLEAN_CONNECT_THRESHOLD=200 * 200,
        CLEAN_CONNECT_RATIO=0.1,
        BORDER_WIDTH=4,
        ELEMENT_INSTRUCTIONS=dict(
            shadda=dict(),
            shadda2=dict(),
            shadda3=dict(),
            semicolon=dict(),
            colon=dict(),
            period=dict(acc=0.9),
            comma=dict(bw=5),
            tanwin=dict(acc=0.7),
            tanwin2=dict(acc=0.7),
            longA=dict(),
            doubleOpen=dict(acc=0.7),
            doubleClose=dict(acc=0.7),
            salla=dict(acc=0.75),
            alayh=dict(acc=0.65),
        ),
        DIVISOR="division",
        WHITE=[255, 255, 255],
        CLEAN_COLOR=dict(
            clean=(255, 255, 255),
            cleanh=(220, 220, 220),
            boxed=(200, 80, 255),
        ),
        CLEAN_MAX_HITS=5000,
        STAGE_ORDER="""
            orig
            gray
            rotated
            normalized
            normalizedC
            histogram
            demargined
            demarginedC
            boxed
            cleanh
            clean
        """.strip().split()
    )
    derived = dict(
        DATA_PATH="{DATA_BASE_DIR}/{DATA_ORG}/{PROJECT}",
        CODE_PATH="{CODE_BASE_DIR}/{CODE_ORG}/{PROJECT}",
        PREOCR_INPUT="{DATA_PATH}/{STEP_PREOCR}/input",
        OCR_INPUT="{DATA_PATH}/{STEP_OCR}/input",
        ELEMENT_DIR="{CODE_PATH}/programs/elements",
    )
    reloadElements = set("""
        ELEMENT_INSTRUCTIONS
        ELEMENT_DIR
        CODE_PATH
        STEP_PREOCR
    """.strip().split())

    def derive(self, parameters):
        c = self.config
        d = self.derived

        for (k, v) in d.items():
            dv = parameters.get(k, v.format(**c))
            c[k] = dv

    def __init__(self, parameters):
        self.derive({})
        self.reconfigure(**parameters)

    def reconfigure(self, **parameters):
        c = self.config

        for (k, v) in sorted(parameters.items()):
            if k not in c:
                sys.stderr.write(f'Unknown parameter "{k}" ignored\n')

        for (k, v) in c.items():
            c[k] = parameters.get(k, v)

        self.derive(parameters)

        for (k, v) in c.items():
            setattr(self, k, parameters.get(k, v))

    def show(self):
        c = self.config
        for k in sorted(c):
            v = getattr(self, k, None)
            print(f"{k:>20} = {v}")
