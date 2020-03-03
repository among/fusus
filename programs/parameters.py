import os

DATA_BASE_DIR = os.path.expanduser('~/Documents')
CODE_BASE_DIR = os.path.expanduser('~/github')
CODE_ORG = 'dirkroorda'
DATA_ORG = "annotation"
PROJECT = "fusus"
DATA_PATH = f"{DATA_BASE_DIR}/{DATA_ORG}/{PROJECT}"
CODE_PATH = f"{CODE_BASE_DIR}/{CODE_ORG}/{PROJECT}"

STEP_PREOCR = "preocr"
STEP_OCR = "ocr"

PREOCR_INPUT = f"{DATA_PATH}/{STEP_PREOCR}/input"
OCR_INPUT = f"{DATA_PATH}/{STEP_OCR}/input"

ELEMENT_DIR = f"{CODE_PATH}/{STEP_PREOCR}/elements"
