"""Run the pipeline on a book

```
python3 -m fusus.convert.tsvFromBook path_to_book_directory
```

The path to the book directory is either absolute
or relative to the current directory.

Use this command to convert books of your own that are not already
in this repo.

This command can be run from any directory.
"""

import sys

from ..book import Book


def doBook(bookPath):

    B = Book(cd=bookPath)

    print("Processing page images and OCRing them")
    B.process()

    print("Exporting data as single TSV file")
    B.exportTsv()


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        doBook(args[0])
    else:
        print("Provide the path to a book directory")
