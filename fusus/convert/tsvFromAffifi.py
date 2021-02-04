"""Run the pipeline on the Fusus Al Hikam (Affifi edition)

```
python3 -m fusus.convert.tsvFromAffifi
```

This command can be run from any directory.
"""

from ..parameters import UR_DIR

from .tsvFromBook import doBook


AFFIFI_PATH = f"{UR_DIR}/affifi"

if __name__ == "__main__":
    doBook(AFFIFI_PATH)
