# `juq`
Query, run, and clean Jupyter notebooks (name is inspired by "`jq` for Jupyter")

[![PyPI version](https://badge.fury.io/py/juq.py.svg)](https://badge.fury.io/py/juq.py)

<!-- toc -->
- [Installation](#installation)
- [Usage](#usage)
    - [`juq cells`](#juq-cells)
    - [`juq merge-outputs`](#juq-merge-outputs)
    - [`juq papermill clean`](#juq-papermill-clean)
    - [`juq papermill run`](#juq-papermill-run)
<!-- /toc -->

## Installation <a id="installation"></a>
```bash
pip install juq.py
```

## Usage <a id="usage"></a>

### `juq cells` <a id="juq-cells"></a>
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

### `juq merge-outputs` <a id="juq-merge-outputs"></a>
Merge consecutive "stream" outputs (e.g. stderr):

<!-- `bmdf -- juq merge-outputs --help` -->
```bash
juq merge-outputs --help
# Usage: juq merge-outputs [OPTIONS] [NB_PATH]
#
#   Merge consecutive "stream" outputs (e.g. stderr).
#
# Options:
#   -i, --in-place                  Modify [NB_PATH] in-place
#   -n, --indent INTEGER            Indentation level for the output notebook
#                                   JSON (default: infer from input)
#   -o, --out-path TEXT             Write to this file instead of stdout
#   -t, --trailing-newline / -T, --no-trailing-newline
#                                   Enforce presence or absence of a trailing
#                                   newline (default: match input)
#   --help                          Show this message and exit.
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

### `juq papermill clean` <a id="juq-papermill-clean"></a>
<!-- `bmdf -- juq papermill clean --help` -->
```bash
juq papermill clean --help
# Usage: juq papermill clean [OPTIONS] [NB_PATH]
#
#   Remove Papermill metadata from a notebook.
#
#   Removes `.metadata.papermill` and
#   `.cells[*].metadata.{papermill,execution,widgets}`.
#
# Options:
#   -i, --in-place                  Modify [NB_PATH] in-place
#   -n, --indent INTEGER            Indentation level for the output notebook
#                                   JSON (default: infer from input)
#   -o, --out-path TEXT             Write to this file instead of stdout
#   -t, --trailing-newline / -T, --no-trailing-newline
#                                   Enforce presence or absence of a trailing
#                                   newline (default: match input)
#   --help                          Show this message and exit.
```

### `juq papermill run` <a id="juq-papermill-run"></a>
<!-- `bmdf -- juq papermill run --help` -->
```bash
juq papermill run --help
# Usage: juq papermill run [OPTIONS] [NB_PATH]
#
#   Run a notebook using Papermill, clean nondeterministic metadata.
#
# Options:
#   -i, --in-place                  Modify [NB_PATH] in-place
#   -n, --indent INTEGER            Indentation level for the output notebook
#                                   JSON (default: infer from input)
#   -o, --out-path TEXT             Write to this file instead of stdout
#   -t, --trailing-newline / -T, --no-trailing-newline
#                                   Enforce presence or absence of a trailing
#                                   newline (default: match input)
#   --help                          Show this message and exit.
```
