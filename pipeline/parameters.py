"""Settings and configuration
"""

from copy import deepcopy


COLORS = dict(
    blackGRS=0,
    blackRGB=(0, 0, 0),
    whiteGRS=255,
    whiteRGB=(255, 255, 255),
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
    orig=("image", None),
    gray=("image", None),
    rotated=("image", None),
    normalized=("image", None),
    normalizedC=("image", None),
    layout=("image", None),
    histogram=("image", None),
    demargined=("image", None),
    demarginedC=("image", None),
    markData=("data", "tsv"),
    boxed=("image", None),
    cleanh=("image", None),
    clean=("image", None),
    ocrData=("data", "tsv"),
)
"""Stages in page processing.

When we process a scanned page,
we produce named intermediate stages,
in this order.

The `...Data` stages are tab separated files with unicode data.
"""

SETTINGS = dict(
    debug=0,
    inDir="in",
    outDir="out",
    interDir="inter",
    marksDir="marks",
    skewBorder=30,
    blurX=41,
    blurY=41,
    marginThresholdX=1,
    marginThresholdY=5,
    marginThreshold2Y=10,
    blockMarginX=12,
    accuracy=0.8,
    connectBorder=4,
    connectThreshold=200 * 200,
    connectRatio=0.1,
    boxBorder=3,
    maxHits=5000,
    bandMain=(0, 0),
    bandInter=(5, 5),
    bandBroad=(-15, 10),
    bandMid=(10, -5),
    bandHigh=(10, 30),
    bandLow=(-10, -10),
)
"""Customizable settings.

These are the settings that can be customized
by calling the `Config` constructor and the
`Config.configure` method.

The default values can be inspected by expanding the source code.

debug
:   Whether to show (intermediate) results.
    If `0`: shows nothing, if `1`: shows end result, if `2`: shows intermediate
    results.

inDir
:   name of the subdirectory with page scans

outDir
:   name of the subdirectory with the final results of the pipeline

interDir
:   name of the subdirectory with the intermediate results of the pipeline

marksDir
:   name of the subdirectory with the marks

skewBorder
:   the  width of the page  margins that will be whitened in order to
    suppress the sharp black triangles introduces by skewing the page

blurX
:   the amount of blur in the X-direction.
    Blurring is needed to get betterskewing and histograms

blurY
:   the amount of blur in the X-direction.
    Blurring is needed to get betterskewing and histograms.

    !!! caution "Amount of Y-blurring"
        Too much vertical blurring will cause the disappearance of horizontal
        bars from the histogram. Footnote  bars will go undetected.

        Too little vertical blurring will result in ragged histograms,
        from which it is difficult to get vertical line boundaries.

marginThresholdX, marginThresholdY
:   used when interpreting histograms.

    **Vertical lines**:

    The histogram for vertical lines will be chunked into groups,
    and only the biggest group will be retained.

    More precisely, values in the histogram for vertical lines that are below
    marginThresholdX will be considered 0. After that, the histogram points
    will be grouped into consecutive chunks with nonzero values.
    The biggest such group will have the vertical lines that contain the page material.
    All other vertical lines will be whitened.

    **Horizontal lines**:

    When histograms for horizontal lines cross marginThresholdY,  it will taken as an
    indication that a line boundary (upper or lower) has been reached.

    !!! hint "Ragged histograms"
        Histograms may be a bit ragged.

        When a histogram dives below the threshold, but jumps above it
        later, without having become zero in the meantime, the last such point
        will be taken as a lower boundary.

        When a histogram jumps above the threshold, but dives below it
        later, without touching zero, and then jumps above the threshold
        again, the latter point will *not* become the upper boundary.

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


MARK_PARAMS = dict(acc="accuracy", cb="connectBorder", r="connectRatio")


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
            info(f"{k:<20} = {settings[k]}", tm=False)
