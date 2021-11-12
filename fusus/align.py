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


def readEditions(versionGiven, casesGiven):
    global version
    global cases
    global alignmentPath
    global A
    global FLK
    global FAF
    global TLK
    global TAF
    global LLK
    global LAF
    global maxLK
    global maxAF
    global getTextLK
    global getTextAF
    global alignment
    global indexLK
    global indexAF
    global decisions

    version = versionGiven
    cases = casesGiven
    alignmentPath = f"{ALIGNMENT_DIR}/alignment{version}.tsv"
    if not os.path.exists(ALIGNMENT_DIR):
        os.makedirs(alignmentPath, exist_ok=True)

    A = {}
    F = {}
    T = {}
    L = {}
    maxSlot = {}

    for (acro, name) in EDITIONS.items():
        A[acro] = use(f"among/fusus/tf/{name}:clone", writing="ara", version=version)
        F[acro] = A[acro].api.F
        T[acro] = A[acro].api.T
        L[acro] = A[acro].api.L
        maxSlot[acro] = F[acro].otype.maxSlot

    FLK = F[LK]
    FAF = F[AF]
    TLK = T[LK]
    TAF = T[AF]
    LLK = L[LK]
    LAF = L[AF]
    maxLK = maxSlot[LK]
    maxAF = maxSlot[AF]

    getTextLK = FLK.lettersn.v
    getTextAF = FAF.lettersn.v

    alignment = []
    indexLK = {}
    indexAF = {}
    decisions = collections.Counter()

    return dict(
        version=version,
        cases=cases,
        alignmentPath=alignmentPath,
        A=A,
        FLK=FLK,
        FAF=FAF,
        TLK=TLK,
        TAF=TAF,
        LLK=LLK,
        LAF=LAF,
        maxLK=maxLK,
        maxAF=maxAF,
        getTextLK=getTextLK,
        getTextAF=getTextAF,
        alignment=alignment,
        indexLK=indexLK,
        indexAF=indexAF,
        decisions=decisions,
    )


def getPosLK(slot):
    (piece, page, line) = TLK.sectionFromNode(slot)
    return f"{page:>03}:{line:>02}"


def getPosAF(slot):
    (page, block, line) = TAF.sectionFromNode(slot)
    return f"{page:>03}:{line:>02}"


def printLines(start=0, end=None):
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
        posLK = getPosLK(iLK) if iLK else ""
        posAF = getPosAF(iAF) if iAF else ""
        lines.append(
            f"{posLK:>6}|{iLK:>5}|{left:<2}|{textLK:>20}|@{d:<2}~{r:3.1f}|{textAF:<20}|{right:>2}|{iAF:>5} {posAF:<6}"
        )
    return "\n".join(lines)


def printAlignment(path, asTsv=False):
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
            fh.write(printLines())
            fh.write("\n")


def printDiff(before, after):
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
    print(printLines(start=len(alignment) - before))
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
            print(f"{iLK:>5} =  {textLK:>20} @{d:>2}~{r:3.1f} {textAF:<20}  = {iAF:>5}")


COMBINE = 4


def getCombis(c):
    combis = []
    for i in range(1, c + 1):
        for j in range(1, c + 1):
            if i != 1 or j != 1:
                combis.append((i, j))
    return tuple(sorted(combis, key=lambda x: (x[0] + x[1], abs(x[0] - x[1]))))


COMBIS = getCombis(COMBINE)
COMBIS


def similar(s1, s2, maxD, minR):
    if s1 == s2:
        return (True, 0, 1.0)

    if maxD == 0 or minR == 1:
        return (False, 77, 0.0)

    d = distance(s1, s2)
    r = ratio(s1, s2)
    return (d <= maxD and r >= minR, d, r)


def catchupAF(start, end):
    for i in range(start, end + 1):
        indexAF[i] = len(alignment)
        alignment.append(("", 0, 99, 0.0, "", i))


def catchupLK(start, end):
    for i in range(start, end + 1):
        indexLK[i] = len(alignment)
        alignment.append((i, "", 99, 0.0, 0, ""))


def doCase(iLK, iAF, debug=False):
    if iLK not in cases:
        return None

    (cLK, cAF) = cases[iLK]
    common = min((cLK, cAF))
    for i in range(max((cLK, cAF))):
        nAlignment = len(alignment)
        if i < common:
            alignment.append((iLK + i, cLK, 88, 0.0, cAF, iAF + i))
            indexLK[iLK + i] = nAlignment
            indexAF[iAF + i] = nAlignment
        elif i < cLK:
            alignment.append((iLK + i, cLK, 88, 0.0, cAF, ""))
            indexLK[iLK + i] = nAlignment
        else:
            alignment.append(("", cLK, 88, 0.0, cAF, iAF + i))
            indexAF[iAF + i] = nAlignment
    if debug:
        print(f"[{iLK}~{iAF}] special case ({cLK}, {cAF})")
    return (iLK + cLK, iAF + cAF)


def findCombi(iLK, iAF, maxD, minR):
    found = None

    for (cLK, cAF) in COMBIS:
        if iLK + cLK > maxLK or iAF + cAF > maxLK:
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
                    alignment.append((iLK + i, cLK, d, r, cAF, iAF + i))
                    indexLK[iLK + i] = nAlignment
                    indexAF[iAF + i] = nAlignment
                elif i < cLK:
                    alignment.append((iLK + i, cLK, d, r, cAF, ""))
                    indexLK[iLK + i] = nAlignment
                elif i < cAF:
                    alignment.append(("", cLK, d, r, cAF, iAF + i))
                    indexAF[iAF + i] = nAlignment
            break
    return found


def compare(iLK, iAF, maxD, minR, debug=False):
    textLK = getTextLK(iLK)
    textAF = getTextAF(iAF)
    (isSimilar, d, r) = similar(textLK, textAF, maxD, minR)
    if isSimilar:
        nAlignment = len(alignment)
        alignment.append((iLK, "", d, r, "", iAF))
        indexLK[iLK] = nAlignment
        indexAF[iAF] = nAlignment
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
            alignment.append((iLK, "", dNext, rNext, "", iAF))
            indexLK[iLK] = nAlignment
            indexAF[iAF] = nAlignment
            if debug:
                print(
                    f"[{iLK}~{iAF}] single comparison failed with distance <= {maxD} and ratio >= {minR}"
                )
            nAlignment = len(alignment)
            alignment.append((iLK + 1, "", dNext, rNext, "", iAF + 1))
            indexLK[iLK] = nAlignment
            indexAF[iAF] = nAlignment
            if debug:
                print(
                    f"[{iLK}~{iAF}] single comparison recovered with distance <= {maxD} and ratio >= {minR}"
                )
            return (iLK + 2, iAF + 2)

    combi = findCombi(iLK, iAF, maxD, minR)
    if combi is not None:
        (cLK, cAF) = combi
        if debug:
            print(
                f"[{iLK}~{iAF}] ({cLK}, {cAF}) comparison with distance <= {maxD} and ratio >= {minR}"
            )
        return (iLK + cLK, iAF + cAF)

    return None


def lookup(iLK, iAF, maxD, minR, start, end, debug=False):
    step = None

    for i in range(start, end + 1):
        prevAlignmentIndex = len(alignment)

        if iAF + i <= maxAF:
            step = compare(iLK, iAF + i, maxD, minR, debug=debug)
            if step:
                if debug:
                    print(f"[{iLK}~{iAF}] right {i}-jump to {iAF + i}")
                thisAlignment = list(alignment[prevAlignmentIndex:])
                alignment[prevAlignmentIndex:] = []

                catchupAF(iAF, iAF + i - 1)
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
            step = compare(iLK + i, iAF, maxD, minR, debug=debug)
            if step:
                if debug:
                    print(f"[{iLK}~{iAF}] left {i}-jump to {iLK + i}")
                thisAlignment = list(alignment[prevAlignmentIndex:])
                alignment[prevAlignmentIndex:] = []

                catchupLK(iLK, iLK + i - 1)
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


def doDiffs(startLK=1, startAF=1, steps=-1, show=False, debug=False):
    alignment.clear()
    decisions.clear()

    lastCase = None
    step = (startLK, startAF)

    it = 0

    def doDiff(iLK, iAF):
        decision = 0
        if iLK > maxLK or iAF > maxAF:
            if iAF < maxAF:
                catchupAF(iAF, maxAF)
            if iLK < maxLK:
                catchupLK(iLK, maxLK)
            decisions[decision] += 1
            return True

        nonlocal lastCase

        decision += 1

        if lastCase != iLK:
            step = doCase(iLK, iAF, debug=debug)
            if step:
                lastCase = iLK
                decisions[decision] += 1
                return step

        step = compare(iLK, iAF, 0, 1.0, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = compare(iLK, iAF, 1, 0.8, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 0, 1.0, 1, 5, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = compare(iLK, iAF, 1, 0.8, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = compare(iLK, iAF, 2, 0.7, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = compare(iLK, iAF, 3, 0.6, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 0, 1.0, 1, 10, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 1, 0.8, 1, 10, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 0, 1.0, 10, 20, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 1, 0.8, 10, 20, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 2, 0.7, 1, 20, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 1, 0.8, 20, 100, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        step = lookup(iLK, iAF, 2, 0.7, 20, 100, debug=debug)
        decision += 1
        if step:
            decisions[decision] += 1
            return step

        return False

    while it != steps:
        it += 1
        step = doDiff(*step)

        if step is True:
            printAlignment("zipLK-AF-complete.txt")
            printAlignment(alignmentPath, asTsv=True)
            print(f"Alignment complete, {len(alignment)} entries.")
            break
        elif step is False:
            printAlignment("zipLK-AF-incomplete.txt")
            print(f"Alignment blocked, {len(alignment)} entries.")
            printDiff(20, 20)
            break

    if show:
        print(printLines())

    for d in sorted(decisions):
        n = decisions[d]
        print(f"{d:>2} taken: {n:>5} x")


LOOKAHEAD = 3


def analyseStretch(start, end):
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


def checkAlignment():
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

    print("\nCOMBINATIONS\n")
    print("What combination alignments are there and how many?")
    for comb in sorted(combinations):
        cs = combinations[comb]
        (left, right) = comb
        print(f"\t({left:>2}, {right:>2}) : {len(cs):>4} x :")
        for (i, c) in enumerate(cs[0:3]):
            print(f"EXAMPLE {i + 1}:")
            print(
                printLines(
                    start=max((1, c - 2)), end=min((len(alignment), c + 2 + max(comb)))
                )
            )
            print("")

    print("\nBAD STRETCHES\n")
    print("How many of which size?\n")
    allSuspects = []
    someBenigns = []
    for (size, starts) in sorted(badStretches.items(), key=lambda x: (-x[0], x[1])):
        suspects = {
            start: size for start in starts if analyseStretch(start, start + size)
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
        print(printLines(max((1, start - 5)), min((len(alignment), end + 5))))
    print(
        f"\nShowing some ({len(someBenigns)}) benign examples"
        if len(someBenigns)
        else "\nNo bad stretches\n"
    )
    for (i, (start, end)) in enumerate(someBenigns):
        print(f"\nBENIGN {i + 1:>2}")
        print(printLines(max((1, start - 2)), min((len(alignment), end + 2))))
