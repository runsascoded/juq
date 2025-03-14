# `juq`
Query, run, and clean/normalize Jupyter notebooks

[![juq.py on PyPI](https://img.shields.io/pypi/v/juq.py?label=juq.py)][juq.py]


<!-- toc -->
- [Installation](#installation)
- [Usage](#usage)
    - [`juq cells`](#juq-cells)
    - [`juq merge-outputs`](#juq-merge-outputs)
    - [`juq papermill clean`](#juq-papermill-clean)
    - [`juq papermill run`](#juq-papermill-run)
    - [`juq renumber`](#juq-renumber)
<!-- /toc -->

## Installation <a id="installation"></a>
```bash
pip install juq.py
```

<!-- `bmdf juq` -->
```bash
juq
# Usage: juq [OPTIONS] COMMAND [ARGS]...
#
# Options:
#   --help  Show this message and exit.
#
# Commands:
#   cells          Slice/Filter cells.
#   merge-outputs  Merge consecutive "stream" outputs (e.g.
#   papermill      Wrapper for Papermill commands (`clean`, `run`).
#   renumber       Renumber cells (and outputs) with non-null...
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
# Usage: juq merge-outputs [OPTIONS] [NB_PATH] [OUT_PATH]
#
#   Merge consecutive "stream" outputs (e.g. stderr).
#
# Options:
#   -a, --ensure-ascii              Octal-escape non-ASCII characters in JSON
#                                   output
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

See also: [test_merge_cell_outputs.py].

[test_merge_cell_outputs.py]: tests/test_merge_cell_outputs.py

### `juq papermill clean` <a id="juq-papermill-clean"></a>
<!-- `bmdf -- juq papermill clean --help` -->
```bash
juq papermill clean --help
# Usage: juq papermill clean [OPTIONS] [NB_PATH] [OUT_PATH]
#
#   Remove Papermill metadata from a notebook.
#
#   Removes `.metadata.papermill` and
#   `.cells[*].metadata.{papermill,execution,widgets}`.
#
# Options:
#   -I, --keep-ids                  Keep cell ids; by default they are removed.
#   -k, --keep-tags / -K, --no-keep-tags
#                                   When a cell's `tags` array is empty, enforce
#                                   its presence or absence in the output.
#   -a, --ensure-ascii              Octal-escape non-ASCII characters in JSON
#                                   output
#   -i, --in-place                  Modify [NB_PATH] in-place
#   -n, --indent INTEGER            Indentation level for the output notebook
#                                   JSON (default: infer from input)
#   -o, --out-path TEXT             Write to this file instead of stdout
#   -t, --trailing-newline / -T, --no-trailing-newline
#                                   Enforce presence or absence of a trailing
#                                   newline (default: match input)
#   --help                          Show this message and exit.
```

See also: [test_papermill_clean.py].

[test_papermill_clean.py]: tests/test_papermill_clean.py

### `juq papermill run` <a id="juq-papermill-run"></a>
<!-- `bmdf -- juq papermill run --help` -->
```bash
juq papermill run --help
# Usage: juq papermill run [OPTIONS] [NB_PATH] [OUT_PATH]
#
#   Run a notebook using Papermill, clean nondeterministic metadata, normalize
#   output streams.
#
# Options:
#   -I, --keep-ids                  Keep cell ids; by default they are removed.
#   -k, --keep-tags / -K, --no-keep-tags
#                                   When a cell's `tags` array is empty, enforce
#                                   its presence or absence in the output.
#   -p, --parameter TEXT            "<k>=<v>" variable to set, while executing
#                                   the notebook
#   -s, --request-save-on-cell-execute
#                                   Request save notebook after each cell
#                                   execution
#   -S, --autosave-cell-every INTEGER
#                                   How often in seconds to autosave the
#                                   notebook during long cell executions (0 to
#                                   disable)
#   -a, --ensure-ascii              Octal-escape non-ASCII characters in JSON
#                                   output
#   -i, --in-place                  Modify [NB_PATH] in-place
#   -n, --indent INTEGER            Indentation level for the output notebook
#                                   JSON (default: infer from input)
#   -o, --out-path TEXT             Write to this file instead of stdout
#   -t, --trailing-newline / -T, --no-trailing-newline
#                                   Enforce presence or absence of a trailing
#                                   newline (default: match input)
#   --help                          Show this message and exit.
```

See also: [test_papermill_run.py].

[test_papermill_run.py]: tests/test_papermill_run.py

### `juq renumber` <a id="juq-renumber"></a>
<!-- `bmdf -- juq renumber --help` -->
```bash
juq renumber --help
# Usage: juq renumber [OPTIONS] [NB_PATH] [OUT_PATH]
#
#   Renumber cells (and outputs) with non-null `execution_count` fields
#   (beginning from 1).
#
#   Simulates the executed cells having been executed in order (e.g. to avoid
#   needing to re-run a whole notebook after rearranging cells that don't depend
#   on one another).
#
# Options:
#   -q, --quiet                     Suppress logging info about each
#                                   `execution_count` update to stderr
#   -a, --ensure-ascii              Octal-escape non-ASCII characters in JSON
#                                   output
#   -i, --in-place                  Modify [NB_PATH] in-place
#   -n, --indent INTEGER            Indentation level for the output notebook
#                                   JSON (default: infer from input)
#   -o, --out-path TEXT             Write to this file instead of stdout
#   -t, --trailing-newline / -T, --no-trailing-newline
#                                   Enforce presence or absence of a trailing
#                                   newline (default: match input)
#   --help                          Show this message and exit.
```

See also: [test_renumber.py].

[test_renumber.py]: tests/test_renumber.py

[juq.py]: https://pypi.org/project/juq.py/
