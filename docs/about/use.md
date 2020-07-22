# Book processing

We will transform scanned pages of a book into Unicode text
following a number of processing steps.

## The express way

In the terminal, `cd` to a book directory (see below) and run

```
python3 -m pipeline.book
```

This will process all scanned pages with default settings.

## With more control and feedback

Copy the notebook `example/do.ipynb` into a book directory (see below).
Run cells in the notebook, and see
[doExample](https://github.com/among/fusus/blob/master/example/doExample.ipynb)
to learn by example how you can configure the processing parameters
and control the processing of pages.

## Book directory

A book directory should have subdirectories:

*   `in`
    Contains mage files (scans at 1800 x2700 pixels approximately)
*   `marks`
    Contains subdirectories with little rectangles copied from the scans
    and saved in individual files at the same resolution.

### Marks

Marks are spots that will be wiped clean wherever they are found.

They are organized in *bands* which are sets of horizontal strokes on the page,
relative to the individual lines.

Marks will only be searched for within the bands they belong to, in order to
avoid false positives.

The `marks` directory may contain the following bands:

name | kind | items | remarks
--- | --- | --- | ---
`high` | marks | arbitrary images | in the upper band of a line
`low` | marks | arbitrary images | in the lower band of a line
`mid` | marks | arbitrary images | in the central, narrow band of a line, with lots of ink
`main` | marks | arbitrary images | in the band where nearly all the letter material is
`broad` | marks | arbitrary images | as `main`, but a bit broader
`inter` | marks | arbitrary images | between the lines
