"""Run the pipeline on the Fusus Al Hikam (Lakhnawi edition)

```
python3 -m fusus.convert.tsvFromLakhnawi
```

This command can be run from any directory.
"""

from ..lakhnawi import Lakhnawi


def main():
    Lw = Lakhnawi()

    print("Reading PDF")
    Lw.getPages(None)

    print("\nExporting TSV")
    Lw.tsvPages(None)

    print("Closing")
    Lw.close()


if __name__ == "__main__":
    main()
