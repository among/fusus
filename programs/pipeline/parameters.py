import sys
import os
import copy
import collections


def merge(dest, updates):
    for k, v in updates.items():
        if (
            k in dest
            and isinstance(dest[k], dict)
            and isinstance(updates[k], collections.Mapping)
        ):
            merge(dest[k], updates[k])
        else:
            dest[k] = updates[k]


class Config:
    default = dict(
        DATA_BASE_DIR=os.path.expanduser("~/Documents"),
        CODE_BASE_DIR=os.path.expanduser("~/github"),
        CODE_ORG="among",
        DATA_ORG="annotation",
        PROJECT="fusus",
        STEP_PREOCR="preocr",
        STEP_OCR="ocr",
        SKEW_BORDER=30,
        ACCURACY=0.8,
        MARGIN_COLOR=(250, 250, 250),
        BAND_THRESHOLD=5,
        BANDS=dict(
            main=dict(isInter=False, color=(40, 40, 40),),
            broad=dict(isInter=False, up=-15, down=10, color=(0, 0, 255),),
            narrow=dict(isInter=False, up=10, down=-5, color=(128, 128, 255),),
            inter=dict(isInter=True, up=5, down=5, color=(255, 200, 200),),
        ),
        CLEAN_HIGHLIGHT=((240, 170, 20), (170, 240, 40), 3),
        CLEAN_CONNECT_THRESHOLD=200 * 200,
        CLEAN_CONNECT_RATIO=0.1,
        BORDER_WIDTH=4,
        BAND="inter",
        MARK_INSTRUCTIONS=dict(
            shadda=dict(),
            shadda2=dict(),
            shadda3=dict(),
            semicolon=dict(),
            colon=dict(),
            period=dict(acc=0.9),
            comma=dict(bw=5, band="narrow"),
            comma2=dict(bw=5, band="narrow"),
            tanwin=dict(acc=0.7),
            tanwin2=dict(acc=0.7),
            longA=dict(),
            doubleOpen=dict(acc=0.7, band="broad"),
            doubleClose=dict(acc=0.7, band="broad"),
            salla=dict(acc=0.75),
            alayh=dict(acc=0.65),
        ),
        DIVISOR="division",
        WHITE=[255, 255, 255],
        CLEAN_COLOR=dict(
            clean=(255, 255, 255), cleanh=(220, 220, 220), boxed=(200, 80, 255),
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
        """.strip().split(),
    )
    derived = dict(
        DATA_PATH="{DATA_BASE_DIR}/{DATA_ORG}/{PROJECT}",
        CODE_PATH="{CODE_BASE_DIR}/{CODE_ORG}/{PROJECT}",
        PREOCR_INPUT="{DATA_PATH}/{STEP_PREOCR}/input",
        OCR_INPUT="{DATA_PATH}/{STEP_OCR}/input",
        MARK_DIR="{CODE_PATH}/programs/marks",
    )
    reloadMarks = set(
        """
        MARK_INSTRUCTIONS
        MARK_DIR
        CODE_PATH
        STEP_PREOCR
    """.strip().split()
    )

    def __init__(self, **parameters):
        """Configuration object.

        It maintains all configuration settings,
        can derive settings from other settings,
        can override settings with given parameters.

        It starts out with a deep copy of the default settings.
        Overrides are merged into this deep copy.

        The settings are available to the rest of the application as members
        of this object. These members are set on the basis of
        the deep copy of current settings.

        Parameters
        ----------
        kwargs: key value pairs
            Configuration settings that override the defaults.
        """
        default = self.default
        self.config = copy.deepcopy(default)
        self.derive({})
        self.reconfigure(**parameters)

    def derive(self, parameters):
        """Compute derived parameters.

        Some settings are derived from other settings.
        If those other settings change, derived settings have to
        be recomputed.

        !!! caution "Overriding a derived setting"
            A derived setting can also be overriden.
            For such a setting, no recomputation will take place,
            so it gets the value that is specified.

            This might lead to an inconsistency between the basic settings
            and the derived, overridden setting.
        """
        c = self.config
        d = self.derived

        for (k, v) in d.items():
            dv = parameters.get(k, v.format(**c))
            c[k] = dv

    def reconfigure(self, reset=False, **parameters):
        """Override configuration settings.

        Configuration settings can be selectively modified.

        Parameters
        ----------
        reset: boolean, optional `False`
            Whether to reset the config settings to their default values
            before merging in the new parameters.
        parameters: key=value pairs
            The keys are settings, the values are new values for those settings.
            If a key is not a known setting, a warning will be generated and the
            key will be ignored. If the value is a dictionary, the value
            will be recursively merged into the existing value.
        """

        default = self.default
        if reset:
            self.config = copy.deepcopy(default)
            self.derive({})

        c = self.config

        for (k, v) in sorted(parameters.items()):
            if k not in c:
                sys.stderr.write(f'Unknown parameter "{k}" ignored\n')

        merge(c, parameters)
        self.derive(parameters)

        for (k, v) in c.items():
            setattr(self, k, parameters.get(k, v))

    def show(self):
        """Show current configuration

        The current configuration will be printed.
        """

        c = self.config
        for k in sorted(c):
            v = getattr(self, k, None)
            sys.stdout.write(f"{k:>20} = {v}\n")
