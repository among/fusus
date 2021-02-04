"""Run the pipeline on a commentary

```
python3 -m fusus.convert.tsvFromCommentary commentary
```

The commentary will be looked up inside the *ur*
directory of the repo.

This command can be run from any directory.
"""

import sys

from ..parameters import UR_DIR

from .tsvFromBook import doBook


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        doBook(f"{UR_DIR}/{args[0]}")
    else:
        print(f"Provide the name of a commentary that resides in {UR_DIR}")
