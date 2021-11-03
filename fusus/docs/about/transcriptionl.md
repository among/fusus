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

name | type | description
--- | --- | ---
`boxl` | int | left x-coordinate of the bounding box of a word
`boxt` | int | top y-coordinate of the bounding box of a word
`boxr` | int | right x-coordinate of the bounding box of a word
`boxb` | int | bottom y-coordinate of the bounding box of a word
`letters` | str | the text of a word in Arabic, unicode, without punctuation
`lettersn` | str | the text of a word in beta code, latin + diacritics
`lettersp` | str | the text of a word in beta code, ascii
`letterst` | str | the text of a word in romanized transcription
`punc` | str | the punctuation and/or space immediately after a word in Arabic, unicode
`punca` | str | the punctuation and/or space immediately after a word in ascii

