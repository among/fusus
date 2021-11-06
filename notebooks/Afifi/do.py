# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python3.9
#     language: python
#     name: python3
# ---

# # OCR Pipeline
#
# We show how to convert a book interactively from pages into tsv and inspect intermediate results.
# This involves performing OCR with Kraken.
# Here we do the Fusus Al Hikam, Afifi edition.
#
# See the documentation of the class [Book](https://among.github.io/fusus/book.html).
#
# There is also a command line interface for running the pipeline, see
# [convert](https://among.github.io/fusus/fusus/convert.html).

# %load_ext autoreload
# %autoreload 2
# !cd `pwd`

from fusus.book import Book

# Initialize the pipeline for processing the pages in this directory.

B = Book(cd="~/github/among/fusus/ur/Afifi")

# Pre-process some pages, to see whether layout and lines are detected properly.
# We do not do OCR yet, and we preserve intermediate results.

page = B.process(pages="52-58", doOcr=False, batch=False)


# We can now go to the directory *inter* and look at all histogram images.
#
# Alternatively, we can inspect one here, e.g. page 57.
#
# * has the layout been detected correctly?
# * do we see the proper line boundaries?

def peek(pageNum):
    page = B.process(pages=pageNum, doOcr=False, batch=False, uptoLayout=True)
    page.show(stage="histogram")
    return page


page = peek(57)

# With the *page* object in hand, we can do more inspections.
#
# Here is the original and a normalized version.

page.show(stage="orig,normalized")

# Now we process these pages completely, including OCR, in batch mode.

page = B.process(pages="52-58", doOcr=True, batch=True)

B.measureQuality(pages="52-58")

B.htmlPages(pages="52-58")

# If the OCR for all the pages has already been executed, you can get the plain HTML text from the TSV pages
# by simply this:

B.htmlPages()


