# Availability

Some sources are not publicly available in this repository.
They are in the directory `_local`, which is excluded from git tracking.

These files might be available upon request to 
[Cornelis van Lit](https://digitalorientalist.com/about-cornelis-van-lit/).

All results obtained from these source materials are publicly available.

!!! caution "No editorial material"
    We have taken care to strip all editorial material from the sources.
    We only process the original, historical portions of the texts.

!!! hint "Intermediate results are reproducible"
    This repository may or may not contain intermediate results, such as
    proofing pages, cleaned images, pages with histograms.
    By running the pipeline again, these results can be reproduced, even without
    recourse to the original materials in the `_local` directory. 

# Fusus Al Hikam

The seminal work is the Fusus Al Hikam (Bezels of Wisdom) by 
[Ibn Arabi 1165-1240](https://en.wikipedia.org/wiki/Ibn_Arabi).

We use two editions, by Lakhnawi and by Afifi.

## Lakhnawi edition

Cornelis obtained by private means a PDF with the typeset text in it.
The text cannot be extracted by normal means due to a range of problems, among
with the unusual encoding of Arabic characters to drive special purpose fonts.

We have reversed engineered the PDF and produced versions in
TSV files, plain text, HTML, Text-Fabric as well as raster images.

The PDF that we worked from is not in the repository, but the results are in the
*ur/Lakhnawi* directory.

The Text-Fabric result is in the `tf/fusus/Lakhnawi` directory, where versioned
releases of the TF data reside.

## Afifi edition

Cornelis obtained a PDF with the text as page images in it.
We have used the `fusus` pipeline to extract the full text involving OCR.

The PDF that we worked from is not in the repository, but the results are in the
*ur/Afifi* directory.

# Commentaries

Cornelis has prepared page images for several commentaries, which we have
carried through the `fusus` pipeline.

The results are in the `ur/xxx` directories, where `xxx` stands for the acronym
of the commentary.

