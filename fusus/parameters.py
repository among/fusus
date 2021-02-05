"""Settings and configuration
"""

import os
from copy import deepcopy
import yaml

HOME = os.path.expanduser('~')
BASE = f"{HOME}/github"
ORG = "among"
REPO = "fusus"
REPO_DIR = f"{BASE}/{ORG}/{REPO}"
PROGRAM_DIR = f"{REPO_DIR}/{REPO}"
LOCAL_DIR = f"{REPO_DIR}/_local"
SOURCE_DIR = f"{LOCAL_DIR}/source"
UR_DIR = f"{REPO_DIR}/ur"
ALL_PAGES = "allpages"

KRAKEN = dict(
    modelPath=f"{REPO_DIR}/model/arabic_generalized.mlmodel"
)

COLORS = dict(
    greyGRS=200,
    blackGRS=0,
    blackRGB=(0, 0, 0),
    whiteGRS=255,
    whiteRGB=(255, 255, 255),
    greenRGB=(0, 255, 0),
    orangeRGB=(255, 127, 0),
    purpleRGB=(255, 0, 127),
    blockRGB=(0, 255, 255),
    letterRGB=(0, 200, 200),
    upperRGB=(0, 200, 0),
    lowerRGB=(200, 0, 0),
    horizontalStrokeRGB=(0, 128, 255),
    verticalStrokeRGB=(255, 128, 0),
    marginGRS=255,
    marginRGB=(200, 200, 200),
    cleanRGB=(255, 255, 255),
    cleanhRGB=(220, 220, 220),
    boxDeleteRGB=(240, 170, 20),
    boxDeleteNRGB=(140, 70, 0),
    boxRemainRGB=(170, 240, 40),
    boxRemainNRGB=(70, 140, 0),
)
"""Named colors. """


BAND_COLORS = dict(
    main=(40, 40, 40),
    inter=(255, 200, 200),
    broad=(0, 0, 255),
    high=(128, 128, 255),
    mid=(128, 255, 128),
    low=(255, 128, 128),
)
"""Band colors.

Each band will be displayed in its own color.
"""

STAGES = dict(
    orig=("image", True, None, None, None),
    gray=("image", False, None, None, None),
    blurred=("image", False, None, None, None),
    normalized=("image", False, None, "proofDir", ""),
    normalizedC=("image", True, None, None, None),
    layout=("image", True, None, None, None),
    histogram=("image", True, None, None, None),
    demargined=("image", False, None, None, None),
    demarginedC=("image", True, None, None, None),
    markData=("data", None, "tsv", None, None),
    boxed=("image", True, None, None, None),
    cleanh=("image", False, None, None, None),
    clean=("image", False, None, "cleanDir", ""),
    binary=("image", False, None, None, None),
    char=("data", None, "tsv", "proofDir", None),
    word=("data", None, "tsv", "outDir", ""),
    line=("data", None, "tsv", "proofDir", "line"),
    proofchar=("link", True, "html", "proofDir", "char"),
    proofword=("link", True, "html", "proofDir", ""),
)
"""Stages in page processing.

When we process a scanned page,
we produce named intermediate stages,
in this order.

The stage data consists of the following bits of information:

* kind: image or data (i.e. tab separated files with unicode data).
* colored: True if colored, False if grayscale, None if not an image
* extension: None if an image file, otherwise the extension of a data file, e.g. `tsv`
"""

SETTINGS = dict(
    debug=0,
    inDir="in",
    outDir="out",
    interDir="inter",
    cleanDir="clean",
    proofDir="proof",
    textDir="text",
    marksDir="marks",
    skewBorderFraction=0.03,
    blurX=21,
    blurY=21,
    marginThresholdX=1,
    contourFactor=0.3,
    contourOffset=0.04,
    peakProminenceY=5,
    peakSignificant=0.1,
    peakTargetWidthFraction=0.5,
    valleyProminenceY=5,
    outerValleyShiftFraction=0.3,
    blockMarginX=12,
    accuracy=0.8,
    connectBorder=4,
    connectThreshold=200 * 200,
    connectRatio=0.1,
    boxBorder=3,
    maxHits=5000,
    bandMain=(5, -5),
    bandInter=(5, 5),
    bandBroad=(-15, 10),
    bandMid=(10, -5),
    bandHigh=(10, 30),
    bandLow=(-10, -10),
    defaultLineHeight=200,
)
"""Customizable settings.

These are the settings that can be customized in several ways.

The values here are the default values.

When the pipeline is run in a book directory, it will look
for a file `parameters.yaml` in the toplevel directory of the book
where these settings can be overridden.

In a program or notebook you can also make last-minute changes to these parameters by
calling the `fusus.book.Book.configure` method which calls the
`Config.configure` method.

The default values can be inspected by expanding the source code.

!!! caution "Two-edged sword"
    When you change a parameter to improve a particular effect on a particular page,
    it may wreak havoc with many other pages.

    When you tweak, take care that you do it locally,
    on a single book, or a single page.

debug
:   Whether to show (intermediate) results.
    If `0`: shows nothing, if `1`: shows end result, if `2`: shows intermediate
    results.

inDir
:   name of the subdirectory with page scans

outDir
:   name of the subdirectory with the final results of the workflow

interDir
:   name of the subdirectory with the intermediate results of the workflow

cleanDir
:   name of the subdirectory with the cleaned, blockwise images of the workflow

marksDir
:   name of the subdirectory with the marks

skewBorder
:   the  width of the page  margins that will be whitened in order to
    suppress the sharp black triangles introduces by skewing the page

blurX
:   the amount of blur in the X-direction.
    Blurring is needed to get better histograms
    To much blurring will hamper the binarization, see e.g. pag 102 in the
    examples directory: if you blur with 41, 41 binarization fails.

blurY
:   the amount of blur in the X-direction.
    Blurring is needed to get betterskewing and histograms.

    !!! caution "Amount of Y-blurring"
        Too much vertical blurring will cause the disappearance of horizontal
        bars from the histogram. Footnote  bars will go undetected.

        Too little vertical blurring will result in ragged histograms,
        from which it is difficult to get vertical line boundaries.

marginThresholdX
:   used when interpreting horizontal histograms.

    When histograms for horizontal lines cross marginThresholdY,  it will taken as an
    indication that a line boundary (upper or lower) has been reached.

contourFactor
:   used when computing left and right contour lines of a page.

    Each horizontal line as a left most black pixel and a rightmost one.
    Together they form the left contour and the right contour of the page.
    The length of each line is the distance between the left contour and right contour
    points on that line.

    However, to be useful, the contour lines must be smoothed.
    We look up and down from each contour point and replace it by the median value of
    the contour points above and below that point.

    How far do we have to look?
    We want to neutralize the interline spaces, so we look up and down for a fraction
    line line height.

    That fraction is specified by this parameter.
    A proxy for the line height is the peak distance.

peakSignificant
:   used when interpreting histograms for line detection

    When we look for significant peaks in a histogram, we determine the max peak height.
    Significant peaks are those that have a height greater than a specific fraction
    of the max peak height. This parameter states that fraction.

peakTargetWidthFraction
:   used when interpreting histograms for line detection
    When we have studied the significant peaks and found the regular distance between
    successive peaks, we use that to pass as the `distance` parameter to the SciPy
    [find_peaks](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html#scipy.signal.find_peaks)
    algorithm. We get the best results if we do not pass the line height itself, but a
    fraction of it. This parameter is that fraction.

peakProminenceY, valleyProminenceY
:   used when interpreting histograms for line detection

    We detect peaks and valleys in the histogram by means of a SciPy algorithm,
    to which we pass a prominence parameter.
    This will leave out minor peaks and valleys.

outerValleyShiftFraction
:   used when interpreting histograms for line detection

    The valleys at the outer ends of the histogram tend to be very broad and hence
    the valleys will be located too far from the actual ink.
    We correct for that by shifting those valleys a fraction of their plateau sizes
    towards the ink. This parameter is that fraction.

defaultLineHeight
:   used for line detection

    After line detection, a value for the line height is found and stored in this
    parameter. The parameter is read when there is only one line on a page, in
    which case the line detection algorithm has too little information.
    If this occurs at the very first calculation of line heights, a fixed
    default value is used.

accuracy
:   When marks are searched for in the page, we get the result in the form
    of a grayscale page where the value in each point reflects how much
    the page in that area resembles the mark.
    Only hits above the value of *accuracy* will be considered.

connectBorder
:   When marks are found, each hit will be inspected:
    is the ink in the hit connected to the ink outside the hit?
    This will be measured in an inner and outer border of the page,
    whose thickness is given by this parameter.

connectThreshold
:   After computing inner and outer borders,
    they will be inverted, so that black has the maximum
    value. Then the inside and outside borders are multiplied pixel wise,
    so that places where they are both black get very high values.
    All places where this product is higher than the value of *connectThreshold*
    are retained for further calculation.

connectRatio
:   After computing the places where inner and outer borders contain
    joint ink, the ratio of such places with respect to the total border size
    is calculated. If that ratio is greater than *connectRatio*,
    the hit counts as connected to its surroundings.
    We have not found a true instance of the mark, and the mark will not be cleaned.

boxBorder
:   The hits after searching for marks will be indicated on the `boxed` stage
    of the page by means of a small coloured border around each hit.
    The width of this border is *boxBorder*.

maxHits
:   When searching for marks, there are usually multiple hits: the place where
    the mark occurs, and some places very nearby.
    The cleaning algorithm will cluster nearby hits and pick the best
    hit per cluster.
    But if the number of hits is very large, it is a sign that the mark
    is not searched with the right accuracy, and clustering will be
    prevented. It would become very expensive, and useless anyway.
    A warning will be issued in such cases.

bandMain
:   Offsets for the `main` band. Given as `(top, bottom)`, with
    `top` and `bottom` positive or negative integers.

    This band covers most of the ink in a line.

    The `main` band is computed from the histogram after which the
    height of the top and bottom boundaries are adjusted relative to the
    values obtained by the histogram algorithm.

    You can adjust these values: higher values move the boundaries down,
    lower values move them up.

    In practice, the adjustments are zero for the main band, while
    all other bands are derived from the main band by applying adjustments.

bandInter
:   Offsets for the `inter` band.

    This band covers most of the white between two lines.

    The `inter` band is computed from the histogram.

bandBroad
:   Offsets for the `broad` band.

    This band s like `main` but covers even more ink in a line.

bandMid
:   Offsets for the `mid` band.

    This band s like `main` but covers the densest part in a line.

bandHigh
:   Offsets for the `high` band.

    This band s like `inter` but covers the upper part of the letters and the white
    space above it.

bandLow
:   Offsets for the `low` band.

    This band s like `inter` but covers the lower part of the letters and the white
    space below it.
"""


MARK_PARAMS = dict(acc="accuracy", bw="connectBorder", r="connectRatio")

CONFIG_FILE = "parameters.yaml"


class Config:
    def __init__(self, tm, **params):
        """Settings manager.

        It will expose all settings as attributes to the rest
        of the application.

        It has methods to collect modified settings from the
        user and apply them.

        The default settings are kept as a separate copy that
        will not be changed in any way.

        User modifications act on the current settings,
        which have been obtained by deep-copying the defaults.

        Parameters
        ----------
        tm: object
            Can display timed info/error messages to the display
        params: dict
            key-value pairs that act as updates for the settings.
            If a value is `None`, the original value will be reinstated.
        """

        self.tm = tm

        # ocr settings
        for (k, v) in KRAKEN.items():
            setattr(self, k, v)

        # colors are fixed
        for (k, v) in COLORS.items():
            setattr(self, k, v)

        # bands
        setattr(self, "colorBand", BAND_COLORS)

        # stages
        setattr(self, "stageOrder", tuple(STAGES))
        setattr(self, "stages", STAGES)

        # marks
        setattr(self, "markParams", MARK_PARAMS)

        # settings
        self.settings = deepcopy(SETTINGS)

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as fh:
                overrides = yaml.load(fh, Loader=yaml.FullLoader)

                # python 3.9 feature
                self.settings |= overrides

        # configure
        self.configure(reset=False, **params)

    def configure(self, reset=False, **params):
        """Updates current settings based on new values.

        User modifications act on the current settings,
        which have been obtained by deep-copying the defaults.

        Parameters
        ----------
        reset: boolean, optional `False`
            If `True`, a fresh deep copy of the defaults will be made
            and that will be the basis for the new current settings.
        params: dict
            key-value pairs that act as updates for the settings.
            If a value is `None`, the original value will be reinstated.
        """

        error = self.tm.error

        if reset:
            self.settings = deepcopy(SETTINGS)

        settings = self.settings

        for (k, v) in params.items():
            if k in SETTINGS:
                settings[k] = SETTINGS[k] if v is None else v
            else:
                error(f"Unknown setting: {k}")

        # band offsets

        offsetBand = {}
        settings["offsetBand"] = offsetBand

        for band in self.colorBand:
            bandOff = f"band{band[0].upper()}{band[1:]}"
            offsetBand[band] = settings[bandOff]

        # deliver as attributes

        for (k, v) in settings.items():
            if not k.startswith("band"):
                setattr(self, k, v)

    def show(self, params=None):
        """Display current settings.

        Parameters
        ----------
        params: str, optional `None`
            If `None`, all settings will be displayed.
            Else it should be a comma-separated string of legal
            parameter names whose values are to be displayed.
        """
        tm = self.tm
        error = tm.error
        info = tm.info

        settings = self.settings

        params = sorted(set(params.split(',')) if params else settings)

        for k in params:
            if k in settings and k not in SETTINGS:
                continue
            if k not in SETTINGS:
                error(f"No such setting: {k}", tm=False)
            info(f"{k:<30} = {settings[k]}", tm=False)
