All functions below are illustrated in the example
[notebook](https://nbviewer.jupyter.org/github/among/fusus/blob/master/example/doExample.ipynb)

# Book

```python
from fusus.book import Book
```

```B = Book()```
:   start up
:   `fusus.book.Book`

```B.showSettings(params)```
:   show settings
:   `fusus.book.Book.showSettings`
:   See also `fusus.parameters`

```B.availableBands()```
:   show the bands defined for this book
:   `fusus.book.Book.availableBands`

```B.availableMarks()```
:   show the marks defined for this book
:   `fusus.book.Book.availableMarks`

```B.availablePages()```
:   show the page ranges contained in this book
:   `fusus.book.Book.availablePages`

```B.configure(**kwargs)```
:   modify settings, bands, marks
:   `fusus.book.Book.configure`
:   See also `fusus.parameters`

```lastPage = B.process()```
:   Process all pages in a book and return a handle
    to the last processed page.
:   `fusus.book.Book.process`

```lastPage = B.process(pages="48-60,67", doOcr=False)```
:   Process all specified pages and return a handle
    to the last processed page. Skip OCR.
:   `fusus.book.Book.process`

# Page

```page = B.process(pages="48", doOcr=False, batch=False)```
:   Process all specified pages and return a handle
    to the last processed page. Skip OCR. Retain intermediate data for inspection.
:   `fusus.book.Book.process`

```page.show(**options)```
:   show the data/images of all intermediate stages that the page went through
    during processing.
:   `fusus.page.Page.show`

```page.show(stage='histogram,cleanh')```
:   show specific stages
:   `fusus.page.Page.show`
:   See also `fusus.parameters.STAGES`

```page.show(stage=stages, band='histogram,cleanh')```
:   show specific stages with specific bands marked/
:   `fusus.page.Page.show`
:   See also `fusus.parameters.BAND_COLORS`

```page.show(stage='boxed', band="high,mid", mark="comma,a")```
:   show specific marks only
:   `fusus.page.Page.show`

```page.write(stage='histogram')```
:   write some or all stages of the page to disk
:   `fusus.page.Page.write`

