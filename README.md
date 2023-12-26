# `juq`
CLI for viewing/slicing Jupyter notebooks (name is inspired by "`jq` for Jupyter")

[![PyPI version](https://badge.fury.io/py/juq.py.svg)](https://badge.fury.io/py/juq.py)

## Installation
```bash
pip install juq.py
```

## Usage

### `juq cells`
Slice/Filter cells:
```bash
juq cells --help
# Usage: juq cells [OPTIONS] CELLS_SLICE [NB_PATH]
#
#   Slice/Filter cells.
#
# Options:
#   -m, --metadata / -M, --no-metadata
#                                   Explicitly include or exclude each cell's
#                                   "metadata" key. If only `-m` is passed, only
#                                   the "metadata" value of each cell is printed
#   -o, --outputs / -O, --no-outputs
#                                   Explicitly include or exclude each cell's
#                                   "outputs" key. If only `-o` is passed, only
#                                   the "outputs" value of each cell is printed
#   -s, --source / -S, --no-source  Explicitly include or exclude each cell's
#                                   "source" key. If only `-s` is passed, the
#                                   source is printed directly (not as JSON)
#   -t, --cell-type TEXT            Only print cells of this type. Recognizes
#                                   abbreviations: "c" for "code", {"m","md"}
#                                   for "markdown", "r" for "raw"
#   --help                          Show this message and exit.
```

### `juq merge-outputs`
Merge consecutive "stream" outputs (e.g. stderr):
```bash
juq merge-outputs --help
# Usage: juq merge-outputs [OPTIONS] [NB_PATH]
#
#   Merge consecutive "stream" outputs (e.g. stderr).
#
# Options:
#   -i, --in-place       Modify [NB_PATH] in-place
#   -o, --out-path TEXT  Write to this file instead of stdout
#   --help               Show this message and exit.
```
e.g.:
```bash
juq merge-outputs -i notebook.ipynb
```
Useful for situations like:
- [jupyter-book#973](https://github.com/executablebooks/jupyter-book/issues/973)
- [nbval#138](https://github.com/computationalmodelling/nbval/issues/138#issuecomment-1869177219)

As of [nbconvert#2089](https://github.com/jupyter/nbconvert/pull/2089), this should be redundant with:

```bash
jupyter nbconvert --coalesce-streams --inplace notebook.ipynb
```

### `juq papermill-clean`
```bash
juq papermill-clean --help
# Usage: juq papermill-clean [OPTIONS] [NB_PATH]
#
#   Remove Papermill metadata from a notebook.
#
#   Removes `.metadata.papermill` and
#   `.cells[*].metadata.{papermill,execution,widgets}`.
#
# Options:
#   -i, --in-place       Modify [NB_PATH] in-place
#   -o, --out-path TEXT  Write to this file instead of stdout
#   --help               Show this message and exit.
```
