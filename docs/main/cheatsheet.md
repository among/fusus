All functions below are illustrated in the example
[notebook](https://nbviewer.jupyter.org/github/among/fusus/blob/master/example/doExample.ipynb)

# Book

```python
from pipeline.book import Book
```

```B = Book()```
:   start up
:   `pipeline.book.Book`

```B.showSettings(params)```
:   show settings
:   `pipeline.book.Book.showSettings`
:   See also `pipeline.parameters`

```B.availableBands()```
:   show the bands defined for this book
:   `pipeline.book.Book.availableBands`

```B.availableMarks()```
:   show the marks defined for this book
:   `pipeline.book.Book.availableMarks`

```B.availablePages()```
:   show the page ranges contained in this book
:   `pipeline.book.Book.availablePages`

```B.configure(**kwargs)```
:   modify settings, bands, marks
:   `pipeline.book.Book.configure`
:   See also `pipeline.parameters`

```lastPage = B.process()```
:   Process all pages in a book and return a handle
    to the last processed page.
:   `pipeline.book.Book.process`

```lastPage = B.process(pages="48-60,67", doOcr=False)```
:   Process all specified pages and return a handle
    to the last processed page. Skip OCR.
:   `pipeline.book.Book.process`

# Page

```page = B.process(pages="48", doOcr=False, batch=False)```
:   Process all specified pages and return a handle
    to the last processed page. Skip OCR. Retain intermediate data for inspection.
:   `pipeline.book.Book.process`

```page.show(**options)```
:   show the data/images of all intermediate stages that the page went through
    during processing.
:   `pipeline.page.Page.show`

```page.show(stage='histogram,cleanh')```
:   show specific stages
:   `pipeline.page.Page.show`
:   See also `pipeline.parameters.STAGES`

```page.show(stage=stages, band='histogram,cleanh')```
:   show specific stages with specific bands marked/
:   `pipeline.page.Page.show`
:   See also `pipeline.parameters.BAND_COLORS`

```page.show(stage='boxed', band="high,mid", mark="comma,a")```
:   show specific marks only
:   `pipeline.page.Page.show`

```page.write(stage='histogram')```
:   write some or all stages of the page to disk
:   `pipeline.page.Page.write`

