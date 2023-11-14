"""
.. include:: docs/about/alignment.md
"""

from Levenshtein import distance, ratio

import collections
import os

from tf.app import use


ORG = "among"
REPO = "fusus"
RELATIVE = "tf"
BASE = os.path.expanduser(f"~/github/{ORG}/{REPO}")
ALIGNMENT_DIR = f"{BASE}/ur/Fusus"

LK = "LK"
AF = "AF"

EDITIONS = {
    LK: "Lakhnawi",
    AF: "Afifi",
}

COMBINE = 4
LOOKAHEAD = 3


def similar(s1, s2, maxD, minR):
    if s1 == s2:
        return (True, 0, 1.0)

    if maxD == 0 or minR == 1:
        return (False, 77, 0.0)

    d = distance(s1, s2)
    r = ratio(s1, s2)
    return (d <= maxD and r >= minR, d, r)


class Alignment:
    """Aligns the words of the LK edition with those of the AF edition.

    The main method is `doDiffs` which produces the alignment table.
    """

    def __init__(self):
        self.getCombis(COMBINE)

    def readEditions(self, version, cases):
        """Read the material of both LK and AF editions.

        Parameters
        ----------
        version: string
            The version number of the source datasets for both editions.
            We assume that both editions are available as Text-Fabric datasets.

        cases: dict
            The special cases defined to help the alignment algorithm through
            difficult spots.

            The dictionary is keyed by LK slot number, and the value is a tuple
            consisting of a corresponding AF slot number, the amount of
            words to collect at the LK side, and the amount of words to collect at
            the AF side.

        Returns
        -------
        None
            But the Alignment object will have attributes set by which
            the other methods are capable of reading the data source.
        """

        self.version = version
        self.cases = cases
        self.alignmentPath = f"{ALIGNMENT_DIR}/alignment{version}.tsv"
        self.alignmentText = f"{ALIGNMENT_DIR}/alignment{version}.txt"
        self.alignmentTextBlocked = f"{ALIGNMENT_DIR}/alignment-incomplete{version}.txt"

        if not os.path.exists(ALIGNMENT_DIR):
            os.makedirs(self.alignmentPath, exist_ok=True)

        A = {}
        F = {}
        T = {}
        L = {}
        maxSlot = {}

        for (acro, name) in EDITIONS.items():
            A[acro] = use(
                f"among/fusus/tf/{name}:clone", writing="ara", version=version
            )
            F[acro] = A[acro].api.F
            T[acro] = A[acro].api.T
            L[acro] = A[acro].api.L
            maxSlot[acro] = F[acro].otype.maxSlot

        self.F_LK = F[LK]
        self.F_AF = F[AF]
        self.T_LK = T[LK]
        self.T_AF = T[AF]
        self.L_LK = L[LK]
        self.L_AF = L[AF]
        self.maxLK = maxSlot[LK]
        self.maxAF = maxSlot[AF]

        self.getTextLK = F[LK].lettersn.v
        self.getTextAF = F[AF].lettersn.v

    def getPosLK(self, slot):
        """Obtain the page and line numbers where a slot in the LK occurs.
        """

        T_LK = self.T_LK

        (piece, page, line) = T_LK.sectionFromNode(slot)
        return f"{page:>03}:{line:>02}"

    def getPosAF(self, slot):
        """Obtain the page and line numbers where a slot in the AF occurs.
        """
        T_AF = self.T_AF

        (page, block, line) = T_AF.sectionFromNode(slot)
        return f"{page:>03}:{line:>02}"

    def printLines(self, start=0, end=None):
        """Print specified entries in the alignment table.

        Parameters
        ----------
        start: integer, optional 0
            Position of first alignment entry that needs to be printed.
            If it is 0 or negative, it starts from the beginning.

        end: integer, optional `None`
            Position of last alignment entry that needs to be printed.
            If it is negative, it indicates a position that much
            before the end of the list.
            If it is absent, it indicates the last line of the list.
        """

        getTextLK = self.getTextLK
        getTextAF = self.getTextAF
        alignment = self.alignment

        if start < 0:
            start = 0
        if end is None or end > len(alignment):
            end = len(alignment)
        lines = []

        lines.append(
            "pag:ln|slot |cc|textLakhnawi        |@ed~rat|textAfifi           |cc| slot|pag:ln"
        )
        lines.append(
            "------|-----|--|--------------------|-------|--------------------|--|-----|------"
        )
        for (iLK, left, d, r, right, iAF) in alignment[start:end]:
            textLK = getTextLK(iLK) if iLK else ""
            textAF = getTextAF(iAF) if iAF else ""
            posLK = self.getPosLK(iLK) if iLK else ""
            posAF = self.getPosAF(iAF) if iAF else ""
            lines.append(
                f"{posLK:>6}|{iLK:>5}|{left:<2}|{textLK:>20}|@{d:<2}~{r:3.1f}|{textAF:<20}|{right:>2}|{iAF:>5} {posAF:<6}"
            )
        return "\n".join(lines)

    def printAlignment(self, path, asTsv=False):
        """Prints the whole alignment table to file.

        Parameters
        ----------
        path: string
            The path name of the file to which the information is printed.

        asTsv: boolean, optional `False
            If False, pretty prints the table to file, using
            `printLines` above.
            If True, write essential data only in tab separated format.
            The essential information is *slot in LK*, *distance*, *slot in AF*
        """
        alignment = self.alignment

        with open(path, "w") as fh:
            if asTsv:
                for item in alignment:
                    fh.write(
                        "\t".join(
                            f"{it:3.1f}" if i == 3 else str(it)
                            for (i, it) in enumerate(item)
                        )
                        + "\n"
                    )
            else:
                fh.write(self.printLines())
                fh.write("\n")

    def printDiff(self, before, after):
        """Print the last alignment entries plus what comes after.

        This function is useful if alignment fails at some point.
        It then shows what happened before the failure and how it looks
        after the failure.

        Parameters
        ----------
        before: integer
            The amount of alignment entries to print.
            They will be picked from the end of the current alignment table.
        after: integer
            The amount of slots after the last alignment entry that
            needs to be shown for each source.
        """
        alignment = self.alignment
        maxLK = self.maxLK
        maxAF = self.maxAF
        getTextLK = self.getTextLK
        getTextAF = self.getTextAF

        print(self.printLines(start=len(alignment) - before))
        print("^" * 67)
        lastLK = None
        lastAF = None
        for c in range(len(alignment) - 1, -1, -1):
            comp = alignment[c]
            if lastLK is None:
                if comp[0]:
                    lastLK = comp[0]
            if lastAF is None:
                if comp[-1]:
                    lastAF = comp[-1]
            if lastLK is not None and lastAF is not None:
                break
        if lastLK is not None and lastAF is not None:
            for i in range(after):
                iLK = lastLK + 1 + i
                iAF = lastAF + 1 + i
                textLK = getTextLK(iLK) if iLK <= maxLK else ""
                textAF = getTextAF(iAF) if iAF <= maxAF else ""
                d = distance(textLK, textAF)
                r = ratio(textLK, textAF)
                print(
                    f"{iLK:>5} =  {textLK:>20} @{d:>2}~{r:3.1f} {textAF:<20}  = {iAF:>5}"
                )

    def printCase(self, iLK, label):
        """Print the alignment entries that belong to a special case.

        Parameters
        ----------
        iLK: integer
            The slot number in LK that triggered a special case.
        label: string
            The kind of issue with this case that you want to report:
            FAILED or MISSING.
        """
        indexLK = self.indexLK
        indexAF = self.indexAF

        cases = self.cases
        case = cases[iLK]
        (iAF, cLK, cAF) = case
        start = min((indexLK[iLK], indexAF[iAF]))
        end = max((indexLK[iLK + cLK + 1], indexAF[iAF + cAF + 1]))
        print(f"{label} CASE: {iLK} vs {iAF}:")
        print(self.printLines(start=start, end=end))

    def getCombis(self, c):
        """Pre-compute a specification of all combinations that might be tried.

        When the alignment fails between single words, we try combinations
        of words left and right in a specific order.
        The result of this function lists the combinations that must be
        tried, where each combination is specified as a tuple
        of the number of words left and the number of words right
        that needs to be taken together for the matching.

        See also: `findCommbi`.
        """
        combis = []
        for i in range(1, c + 1):
            for j in range(1, c + 1):
                if i != 1 or j != 1:
                    combis.append((i, j))
        self.combis = tuple(
            sorted(combis, key=lambda x: (x[0] + x[1], abs(x[0] - x[1])))
        )

    def catchupAF(self, start, end):
        """Move the current position in the AF edition forward.

        While doing so, it adds an entry to the alignment table
        for each time the position is shifted by one.

        Parameters
        ----------
        start: integer
            From where to start shifting
        end: integer
            Where to end shifting
        """
        indexAF = self.indexAF
        alignment = self.alignment

        for i in range(start, end + 1):
            indexAF[i] = len(alignment)
            alignment.append(("", 0, 99, 0.0, "", i))

    def catchupLK(self, start, end):
        """Move the current position in the LK edition forward.

        While doing so, it adds an entry to the alignment table
        for each time the position is shifted by one.

        Parameters
        ----------
        start: integer
            From where to start shifting
        end: integer
            Where to end shifting
        """
        indexLK = self.indexLK
        alignment = self.alignment

        for i in range(start, end + 1):
            indexLK[i] = len(alignment)
            alignment.append((i, "", 99, 0.0, 0, ""))

    def doCase(self, iLK, iAF, debug=False):
        """Deal with a special case.

        Parameters
        ----------
        iLK: integer
            Current position in LK edition.
            A case is triggered when iLK is equal
            to a key in the cases table and if the same case
            has not already been applied.
            This last condition is relevant for special
            cases where the number of LK words that must be
            combined is 0. In that case, the current LK
            position does not shift, and we would be in an
            infinite loop.
        iAF: integer
            Current position in AF edition.
            If a case is triggered by iLK, but the AF position
            specified in the case does not match `iAF`,
            the case is skipped and is reported as a failed case.
        """
        indexLK = self.indexLK
        indexAF = self.indexAF
        alignment = self.alignment
        usedCases = self.usedCases
        failedCases = self.failedCases

        cases = self.cases

        if iLK not in cases:
            return None

        (givenIAF, cLK, cAF) = cases[iLK]
        if givenIAF != iAF:
            failedCases.add(iLK)
            return None

        usedCases.add(iLK)
        common = min((cLK, cAF))
        for i in range(max((cLK, cAF))):
            nAlignment = len(alignment)
            if i < common:
                indexLK[iLK + i] = nAlignment
                indexAF[iAF + i] = nAlignment
                alignment.append((iLK + i, cLK, 88, 0.0, cAF, iAF + i))
            elif i < cLK:
                indexLK[iLK + i] = nAlignment
                alignment.append((iLK + i, cLK, 88, 0.0, cAF, ""))
            else:
                indexAF[iAF + i] = nAlignment
                alignment.append(("", cLK, 88, 0.0, cAF, iAF + i))
        if debug:
            print(f"[{iLK}~{iAF}] special case ({cLK}, {cAF})")
        return (iLK + cLK, iAF + cAF)

    def findCombi(self, iLK, iAF, maxD, minR):
        """Tries out all possible combinations at this point until success.

        This is typically called when a direct match at the current slots
        in LK and AF fail.

        We are going to take together small amounts of words and match
        them instead. As soon as we have a match, we break out of the loop
        and use step to the new positions.

        See also: `getCombis` and `compare`.

        Parameters
        ----------
        iLK: integer
            Current slot position in LK edition
        iAF: integer
            Current slot position in AF edition
        maxD: integer
            maximum edit distance that we allow for the comparisons to succeed
        minR: integer
            minimum similarity ratio that we require for the comparisons to succeed
        """
        combis = self.combis
        maxLK = self.maxLK
        maxAF = self.maxAF
        getTextLK = self.getTextLK
        getTextAF = self.getTextAF
        alignment = self.alignment
        indexLK = self.indexLK
        indexAF = self.indexAF

        found = None

        for (cLK, cAF) in combis:
            if iLK + cLK > maxLK or iAF + cAF > maxAF:
                continue
            textLK = "".join(getTextLK(iLK + i) for i in range(cLK))
            textAF = "".join(getTextAF(iAF + i) for i in range(cAF))
            (isSimilar, d, r) = similar(textLK, textAF, maxD, minR)
            if isSimilar:
                found = (cLK, cAF)
                common = min((cLK, cAF))
                for i in range(max((cLK, cAF))):
                    nAlignment = len(alignment)
                    if i < common:
                        indexLK[iLK + i] = nAlignment
                        indexAF[iAF + i] = nAlignment
                        alignment.append((iLK + i, cLK, d, r, cAF, iAF + i))
                    elif i < cLK:
                        indexLK[iLK + i] = nAlignment
                        alignment.append((iLK + i, cLK, d, r, cAF, ""))
                    elif i < cAF:
                        indexAF[iAF + i] = nAlignment
                        alignment.append(("", cLK, d, r, cAF, iAF + i))
                break
        return found

    def compare(self, iLK, iAF, maxD, minR, debug=False):
        """Does a full comparison at a location, including between combinations.

        First a direct match between the words at the current positions in
        the LK and AF editions is tried. If that fails,
        combinations of words from those points onward are tried.

        See also: `getCombis` and `findCombi`.

        Parameters
        ----------
        iLK: integer
            Current slot position in LK edition
        iAF: integer
            Current slot position in AF edition
        maxD: integer
            maximum edit distance that we allow for the comparisons to succeed
        minR: integer
            minimum similarity ratio that we require for the comparisons to succeed
        debug: boolean, optional `False`
            If True, print a statement indicating the result of the comparison.
        """
        maxLK = self.maxLK
        maxAF = self.maxAF
        getTextLK = self.getTextLK
        getTextAF = self.getTextAF
        alignment = self.alignment
        indexLK = self.indexLK
        indexAF = self.indexAF

        textLK = getTextLK(iLK)
        textAF = getTextAF(iAF)
        (isSimilar, d, r) = similar(textLK, textAF, maxD, minR)
        if isSimilar:
            nAlignment = len(alignment)
            indexLK[iLK] = nAlignment
            indexAF[iAF] = nAlignment
            alignment.append((iLK, "", d, r, "", iAF))
            if debug:
                print(
                    f"[{iLK}~{iAF}] single comparison with distance <= {maxD} and ratio >= {minR}"
                )
            return (iLK + 1, iAF + 1)

        if iLK < maxLK and iAF < maxAF:
            textLK = getTextLK(iLK + 1)
            textAF = getTextAF(iAF + 1)
            (isSimilarNext, dNext, rNext) = similar(textLK, textAF, maxD, minR)
            if isSimilarNext:
                nAlignment = len(alignment)
                indexLK[iLK] = nAlignment
                indexAF[iAF] = nAlignment
                alignment.append((iLK, "", dNext, rNext, "", iAF))
                if debug:
                    print(
                        f"[{iLK}~{iAF}] single comparison failed with distance <= {maxD} and ratio >= {minR}"
                    )
                nAlignment = len(alignment)
                indexLK[iLK + 1] = nAlignment
                indexAF[iAF + 1] = nAlignment
                alignment.append((iLK + 1, "", dNext, rNext, "", iAF + 1))
                if debug:
                    print(
                        f"[{iLK}~{iAF}] single comparison recovered with distance <= {maxD} and ratio >= {minR}"
                    )
                return (iLK + 2, iAF + 2)

        combi = self.findCombi(iLK, iAF, maxD, minR)
        if combi is not None:
            (cLK, cAF) = combi
            if debug:
                print(
                    f"[{iLK}~{iAF}] ({cLK}, {cAF}) comparison with distance <= {maxD} and ratio >= {minR}"
                )
            return (iLK + cLK, iAF + cAF)

        return None

    def lookup(self, iLK, iAF, maxD, minR, start, end, debug=False):
        """Performs a jump in both editions.

        Typically invoked when comparison at the current locations fail,
        even after having tried combinations.

        We compare the current word in one edition with those from a certain
        interval in the other edition. And vice versa, alternately.
        of subsequent words.

        Parameters
        ----------
        iLK: integer
            Current slot position in LK edition
        iAF: integer
            Current slot position in AF edition
        maxD: integer
            maximum edit distance that we allow for the comparisons to succeed
        minR: integer
            minimum similarity ratio that we require for the comparisons to succeed
        start: integer
            first position in the other edition where we start comparing
        end: integer
            last position in the other edition where we stop comparing
        debug: boolean, optional `False`
            If True, print a statement indicating the result of the lookup.
        """
        maxLK = self.maxLK
        maxAF = self.maxAF
        alignment = self.alignment
        indexLK = self.indexLK
        indexAF = self.indexAF

        step = None

        for i in range(start, end + 1):
            prevAlignmentIndex = len(alignment)

            if iAF + i <= maxAF:
                step = self.compare(iLK, iAF + i, maxD, minR, debug=debug)
                if step:
                    if debug:
                        print(f"[{iLK}~{iAF}] right {i}-jump to {iAF + i}")
                    thisAlignment = list(alignment[prevAlignmentIndex:])
                    alignment[prevAlignmentIndex:] = []

                    self.catchupAF(iAF, iAF + i - 1)
                    for thisComp in thisAlignment:
                        nAlignment = len(alignment)
                        thisLK = thisComp[0]
                        thisAF = thisComp[-1]
                        if thisLK:
                            indexLK[thisLK] = nAlignment
                        if thisAF:
                            indexAF[thisAF] = nAlignment
                        alignment.append(thisComp)
                    break

            if iLK + i <= maxLK:
                step = self.compare(iLK + i, iAF, maxD, minR, debug=debug)
                if step:
                    if debug:
                        print(f"[{iLK}~{iAF}] left {i}-jump to {iLK + i}")
                    thisAlignment = list(alignment[prevAlignmentIndex:])
                    alignment[prevAlignmentIndex:] = []

                    self.catchupLK(iLK, iLK + i - 1)
                    for thisComp in thisAlignment:
                        nAlignment = len(alignment)
                        thisLK = thisComp[0]
                        thisAF = thisComp[-1]
                        if thisLK:
                            indexLK[thisLK] = nAlignment
                        if thisAF:
                            indexAF[thisAF] = nAlignment
                        alignment.append(thisComp)
                    break
        return step

    def doDiffs(self, startLK=1, startAF=1, steps=-1, show=False, debug=False):
        """Main loop of the alignment process.

        Without optional parameters, performs the whole alignment until
        it is completed or fails.

        But you can also run a few alignment steps, from arbitrary positions
        and record the decision steps. This is handy for debugging and
        exploring.

        !!! hint "`doDiff`"
            This function defines an inner function `doDiff`, which
            contains the logic of a single alignment step.
            That function `doDiff` issues a sequence of `compare` and `lookup`
            commands with various strictnesses and various jump sizes,
            which will be tried in order.

            Here you can finetune the amount of looseness you allow in a comparison
            before jumping from that position.
            You can first compare strictly, then jump away a short distance while
            still comparing strictly, and then start comparing more loosely, and
            then jump away a longer distance, possibly a bit more loosely.
            That is a matter of trial and error.

            The current implementation of `doDiff` matches the present LK and AF well,
            especially in conjunction with the special cases that have been defined.

        Parameters
        ----------
        startLK: integer, optional 1
            Start position in LK edition. If not passed, starts from the beginning.
        startAF: integer, optional 1
            Start position in AF edition. If not passed, starts from the beginning.
        steps: integer, optional `-1`
            The number of alignment steps to perform.
            If not passed or -1, there is no limit on the steps.
        show: boolean, optional False
            If True, prints the resulting alignment table to the screen.
            Only do this when you produce a small part of the alignment table!
            maximum edit distance that we allow for the comparisons to succeed
        debug: boolean, optional `False`
            If True, print a statement indicating the result of the each decision
            that has been taken during the alignment process.
        """
        maxLK = self.maxLK
        maxAF = self.maxAF
        cases = self.cases
        alignmentPath = self.alignmentPath
        alignmentText = self.alignmentText
        alignmentTextBlocked = self.alignmentTextBlocked

        self.alignment = []
        self.indexLK = {}
        self.indexAF = {}
        self.decisions = collections.Counter()
        self.usedCases = set()
        self.failedCases = set()

        alignment = self.alignment
        indexLK = self.indexLK
        decisions = self.decisions
        usedCases = self.usedCases
        failedCases = self.failedCases

        lastCase = None
        step = (startLK, startAF)

        it = 0

        def doDiff(iLK, iAF):
            decision = 0
            if iLK > maxLK or iAF > maxAF:
                if iAF < maxAF:
                    self.catchupAF(iAF, maxAF)
                if iLK < maxLK:
                    self.catchupLK(iLK, maxLK)
                decisions[decision] += 1
                return True

            nonlocal lastCase

            decision += 1

            if lastCase != iLK:
                step = self.doCase(iLK, iAF, debug=debug)
                if step:
                    lastCase = iLK
                    decisions[decision] += 1
                    return step

            step = self.compare(iLK, iAF, 0, 1.0, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.compare(iLK, iAF, 1, 0.8, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 0, 1.0, 1, 5, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.compare(iLK, iAF, 1, 0.8, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.compare(iLK, iAF, 2, 0.7, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.compare(iLK, iAF, 3, 0.6, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 0, 1.0, 1, 10, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 1, 0.8, 1, 10, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 0, 1.0, 10, 20, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 1, 0.8, 10, 20, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 2, 0.7, 1, 20, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 1, 0.8, 20, 100, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            step = self.lookup(iLK, iAF, 2, 0.7, 20, 100, debug=debug)
            decision += 1
            if step:
                decisions[decision] += 1
                return step

            return False

        while it != steps:
            it += 1
            step = doDiff(*step)

            if step is True:
                self.printAlignment(alignmentText)
                self.printAlignment(alignmentPath, asTsv=True)
                print(f"Alignment complete, {len(alignment)} entries.")
                break
            elif step is False:
                self.printAlignment(alignmentTextBlocked)
                print(f"Alignment blocked, {len(alignment)} entries.")
                self.printDiff(20, 20)
                break

        endLK = startLK if len(indexLK) == 0 else max(indexLK)
        possibleCases = set(range(startLK, endLK + 1))
        casesSet = set(cases)
        relevantCases = casesSet & possibleCases
        missedCases = relevantCases - usedCases - failedCases

        if failedCases:
            for iLK in sorted(failedCases):
                self.printCase(iLK, "FAILED")
        if missedCases:
            for iLK in sorted(missedCases):
                self.printCase(iLK, "MISSED")

        if not failedCases and not missedCases:
            if not relevantCases:
                print("No special cases defined for this stretch")
            else:
                print(
                    f"Special cases: all relevant {len(relevantCases)} cases "
                    "defined, encountered, and applied"
                )

        if show:
            print(self.printLines())

        for d in sorted(decisions):
            n = decisions[d]
            print(f"{d:>2} taken: {n:>5} x")

    def analyseStretch(self, start, end):
        """Analyse a stretch in the alignment table and reports whether it is suspect.

        Stretches are suspect if they contain both a number entries where an LK
        word is missing, and a number of entries where an AF word is missing.

        This is usually an indication that the alignment has gone out of sync.

        Parameters
        ----------
        start: integer
            Index in the alignment list where to start
        end: integer
            Index in the alignment list where to stop
        """
        alignment = self.alignment

        total = 0
        good = 0
        onlyLK = 0
        onlyAF = 0

        for (iLK, left, d, r, right, iAF) in alignment[start : end + 1]:
            total += 1
            if not iLK:
                onlyAF += 1
            if not iAF:
                onlyLK += 1
            if d == 0:
                good += 1

        suspect = onlyAF > 1 and onlyLK > 1 and onlyAF + onlyLK > 5
        return suspect

    def check(self):
        """Comprehensive quality assessment of the alignment table.

        Reports various statistics on how close the matches are overall.

        Checks the minimum requirement of sanity:
        All words in the LK must occur without duplications in the right order
        int the alignment table. Same for the AF words.

        Reports where the combinations are: the cases where more than one word
        in the LK has matched with more than one word in the AF.
        Or where single words have been forced to match, or where words
        in one edition have no counterpart in the other edition.
        Gives at most three examples of all distinct combination patterns.

        Identifies bad stretches: chunks of entries within the alignment
        table where words do not match for various reasons.
        The identification is a bit loose in the sense that bad stretches
        with a single perfect match in between are combined.

        Some bad stretches are suspect (see `analyseStretch`).
        All suspect stretches are shown, and at most three examples
        of the benign (non-suspect) bad stretches are shown.
        """
        maxLK = self.maxLK
        maxAF = self.maxAF
        alignment = self.alignment

        errors = {}
        prevILK = 0
        prevIAF = 0

        where = collections.Counter()
        agreement = collections.Counter()
        badStretches = collections.defaultdict(lambda: [])
        combinations = collections.defaultdict(lambda: [])

        startBad = 0
        startCombi = 0
        nCombi = 0

        for (c, (iLK, left, d, r, right, iAF)) in enumerate(alignment):
            thisBad = d > 0 or not iLK or not iAF
            hasLeft = left != ""
            hasRight = right != ""

            # a good line between bad lines is counted as bad
            if not thisBad and startBad:
                nextGood = True
                for j in range(1, LOOKAHEAD + 1):
                    if c + j < len(alignment):
                        compJ = alignment[c + j]
                        if compJ[2] > 0 or not compJ[0] or not compJ[-1]:
                            nextGood = False
                            break
                if not nextGood:
                    thisBad = True
            if startBad:
                if not thisBad:
                    badStretches[c - startBad].append(startBad)
                    startBad = 0
            else:
                if thisBad:
                    startBad = c

            if startCombi and nCombi == c - startCombi:
                startCombi = 0
                nCombi = 0
            if startCombi == 0:
                thisCombi = hasLeft and left > 1 or hasRight and right > 1
                if thisCombi:
                    combinations[(left, right)].append(c)
                    startCombi = c
                    nCombi = max((left, right))

            agreement[d] += 1

            if iLK:
                if iLK != prevILK + 1:
                    errors.setdefault("wrong iLK", []).append(
                        f"{c:>5}: Expected {prevILK + 1}, found {iLK}"
                    )
                prevILK = iLK
                if iAF:
                    where["both"] += 1
            else:
                where[AF] += 1
            if iAF:
                if iAF != prevIAF + 1:
                    errors.setdefault("wrong iAF", []).append(
                        f"{c:>5}: Expected {prevIAF + 1}, found {iAF}"
                    )
                prevIAF = iAF
            else:
                where[LK] += 1

        if startBad:
            badStretches[len(alignment) - startBad].append(startBad)

        if prevILK < maxLK:
            errors.setdefault("missing iLKs at the end", []).append(
                f"last is {prevILK}, expected {maxLK}"
            )
        elif prevILK > maxLK:
            errors.setdefault("too many iLKs at the end", []).append(
                f"last is {prevILK}, expected {maxLK}"
            )
        if prevIAF < maxAF:
            errors.setdefault("missing iAFs at the end", []).append(
                f"last is {prevIAF}, expected {maxAF}"
            )
        elif prevIAF > maxAF:
            errors.setdefault("too many iAFs at the end", []).append(
                f"last is {prevIAF}, expected {maxAF}"
            )

        print("\nSANITY\n")
        if not errors:
            print("All OK")
        else:
            for (kind, msgs) in errors.items():
                print(f"ERROR {kind} ({len(msgs):>5}x):")
                for msg in msgs[0:10]:
                    print(f"\t{msg}")
                if len(msgs) > 10:
                    print(f"\t ... and {len(msgs) - 10} more ...")

        print("\nAGREEMENT\n")
        print("Where are the words?\n")
        print(f"\t{LK}-only: {where[LK]:>5} slots")
        print(f"\t{AF}-only: {where[AF]:>5} slots")
        print(f"\tboth:    {where['both']:>5} slots")

        print("\nHow well is the agreement?\n")
        for (d, n) in sorted(agreement.items()):
            print(f"edit distance {d:>3} : {n:>5} words")
        print("NB: 88 are special cases that have been declared explicitly")
        print("NB: 99 are words that have no counterpart in the other edition")

        print("\nCOMBINATIONS\n")
        print("What combination alignments are there and how many?")
        for comb in sorted(combinations):
            cs = combinations[comb]
            (left, right) = comb
            print(f"\t({left:>2}, {right:>2}) : {len(cs):>4} x :")
            for (i, c) in enumerate(cs[0:3]):
                print(f"EXAMPLE {i + 1}:")
                print(
                    self.printLines(
                        start=max((1, c - 2)),
                        end=min((len(alignment), c + 2 + max(comb))),
                    )
                )
                print("")

        print("\nBAD STRETCHES\n")
        print("How many of which size?\n")
        allSuspects = []
        someBenigns = []
        for (size, starts) in sorted(badStretches.items(), key=lambda x: (-x[0], x[1])):
            suspects = {
                start: size
                for start in starts
                if self.analyseStretch(start, start + size)
            }
            benigns = {start: size for start in starts if start not in suspects}
            allSuspects.extend(
                [(start, start + size) for (start, size) in suspects.items()]
            )
            someBenigns.extend(
                [(start, start + size) for (start, size) in list(benigns.items())[0:3]]
            )
            examples = ", ".join(str(start) for start in list(suspects.keys())[0:3])
            if not suspects:
                examples = ", ".join(str(start) for start in list(benigns.keys())[0:3])
            print(
                f"bad stretches of size {size:>3} : {len(suspects):>4} suspect of total {len(starts):>4} x see e.g. {examples}"
            )

        print(
            f"\nShowing all {len(allSuspects)} inversion suspects"
            if len(allSuspects)
            else "\nNo suspect bad stretches\n"
        )
        for (i, (start, end)) in enumerate(reversed(allSuspects)):
            print(f"\nSUSPECT {i + 1:>2}")
            print(self.printLines(max((1, start - 5)), min((len(alignment), end + 5))))
        print(
            f"\nShowing some ({len(someBenigns)}) benign examples"
            if len(someBenigns)
            else "\nNo bad stretches\n"
        )
        for (i, (start, end)) in enumerate(someBenigns):
            print(f"\nBENIGN {i + 1:>2}")
            print(self.printLines(max((1, start - 2)), min((len(alignment), end + 2))))
