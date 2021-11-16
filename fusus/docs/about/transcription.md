# Lakhnawi transcription

The Text-Fabric data is derived from the Lakhnawi PDF by reverse engineering.
The PDF is a textual PDF with an unusual usage of fonts to obtain desired effects with
ligatures and diacritics.

# Divisions

The text is divided into the following chunks

## Piece

**Section level 1**

Logical unit, corresponding to the main division of the work: *bezel*.
(The title of the work is: *bezels* of wisdom.)

Some pieces are in fact introductory chapters, and not the *bezels* of the
main work.

**Features**

name | type | description
--- | --- | ---
`n` | int | sequence number of a piece, starting with 1
`np` | int | sequence number of a proper content piece, i.e. a *bezel*
`title` | str | title of a piece

## Page

**Section level 2**

Physical unit: a printed page.

**Features**

name | type | description
--- | --- | ---
`n` | int | sequence number of a page, starting with 1

## Line

**Section level 3**

Physical unit: a printed line within a page.

**Features**

name | type | description
--- | --- | ---
`n` | int | sequence number of a page, starting with 1

## Column

Logical/physical unit: a column within a line.

Note that the page is not divided into columns.
Some lines are divided into columns in
hemistic poems. See `fusus.lakhnawi.Lakhnawi.columns`.

## Span

Logical/physical unit: a strectch of text with the same writing direction.
Whenever the writing direction reverses, a new span is started.


**Features**

name | type | description
--- | --- | ---
`n` | int | sequence number of a span within a column or line
`dir` | str | writing direction of a span; either `r` or `l`

## Sentence

Logical unit: a sentence, defined by the full-stop marker.
Whenever the writing direction reverses, a new span is started.


**Features**

name | type | description
--- | --- | ---
`n` | int | sequence number of a span within a column or line

## Word

Logical/physical unit: individual words in as far they are separated
by whitespace.

!!! caution "Imperfect whitespace detection"
    We do not guarantee that whitespace has been detected
    perfectly.
    So we do miss word boundaries on the one hand, and we
    have spurious word boundaries on the other hand.

**Features**

We have features that contain the text. The following features contain
the Lakhnawi text.

name | type | description
--- | --- | ---
`letters` | str | the text of a word in Arabic, unicode, without punctuation
`lettersn` | str | the text of a word in beta code, latin + diacritics
`lettersp` | str | the text of a word in beta code, ascii
`letterst` | str | the text of a word in romanized transcription
`punc` | str | the punctuation and/or space immediately after a word in Arabic, unicode
`punca` | str | the punctuation and/or space immediately after a word in ascii

The Afifi text is stored in analogous features:

name | type | description
--- | --- | ---
`letters_af` | str | the text of a word in Arabic, unicode, without punctuation
`lettersn_af` | str | the text of a word in beta code, latin + diacritics
`lettersp_af` | str | the text of a word in beta code, ascii
`letterst_af` | str | the text of a word in romanized transcription
`punc_af` | str | the punctuation and/or space immediately after a word in Arabic, unicode
`punca_af` | str | the punctuation and/or space immediately after a word in ascii

There is also information about the location of the AF words in their edition:

name | type | description
--- | --- | ---
`page_af` | int | the page number in the AF edition of this word
`line_af` | int | the line number in the AF edition of this word

There are extra features that contain information about the alignment between
the LK words and the AF words.
Some features identify the slots in the individual datasets before the merge.
These datasets contain the box/confidence information of the words.
We decided not to take this information with us in the merger.

name | type | description
--- | --- | ---
`slot_lk` | int | the slot number of this word in the `fususl` dataset
`slot_af` | int | the slot number of this word in the `fususa` dataset
`combine_lk` | int | if the slot is part of a combination of LK words that has been aligned, this is the number of words in that combination 
`combine_af` | int | if the slot is part of a combination of AF words that has been aligned, this is the number of words in that combination 
`editdistance` | int | the edit distance between the combination/word on the LK side and the combination/word on the AF side
`ratio` | int | the similarity ratio between the combination/word on the LK side and the combination/word on the AF side. 10 is completely similar. 0 is completely dissimilar.

The Lakhnawi text has been enriched with several features by Cornelis van Lit.
In fact, the features `letters`, `lettersn`, `lettersp`, `letterst` derive
from that enrichment.

name | type | description
--- | --- | ---
`raw` | str | the raw text of the word as in the `fususl` dataset
`puncb` | str | punctuation immediately before a word (Arabic unicode)
`puncba` | str | punctuation immediately before a word (Ascii)
`qunawims` | str | on which folio of the oldest manuscript, penned by Qunawi himself, is this word attested?
`poetrymeter` | str | meter in which this verse is written
`poetryverse` | int | word is start of a verse of poetry, value is the number of the verse
`fass` | int | number of the piece (bezel) that the word belongs to
`lwcvl` | str | personal notes by Cornelis van Lit
`quran` | str | word is part of a quran citation (sura:aya)
