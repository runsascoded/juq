# `juq`
Query, run, and clean/normalize Jupyter notebooks

[![juq_py on PyPI](https://img.shields.io/pypi/v/juq_py?label=juq_py)][juq_py]


<!-- `toc` -->
- [Installation](#installation)
- [Usage](#usage)
    - [`juq nb`](#juq-nb)
        - [`juq nb fmt`](#juq-nb-fmt)
        - [`juq nb run`](#juq-nb-run)
        - [`juq nb clean`](#juq-nb-clean)
    - [`juq cells`](#juq-cells)
    - [`juq merge-outputs`](#juq-merge-outputs)
    - [`juq papermill`](#juq-papermill)
    - [`juq renumber`](#juq-renumber)

## Installation <a id="installation"></a>
```bash
pip install juq_py
```

<!-- `bmdf -- juq --help` -->
```bash
juq --help
# Usage: juq [OPTIONS] COMMAND [ARGS]...
#
# Options:
#   --help  Show this message and exit.
#
# Commands:
#   cells          Slice/Filter cells.
#   merge-outputs  Merge consecutive "stream" outputs (e.g.
#   nb             Notebook transformation commands (fmt, run, clean, etc.).
#   papermill      Wrapper for Papermill commands (`clean`, `run`).
#   renumber       Renumber cells (and outputs) with non-null...
```


## Usage <a id="usage"></a>

### `juq nb` <a id="juq-nb"></a>
Unified command group for notebook transformations:

<!-- `bmdf -- juq nb --help` -->
```bash
juq nb --help
# Usage: juq nb [OPTIONS] COMMAND [ARGS]...
#
#   Notebook transformation commands (fmt, run, clean, etc.).
#
# Options:
#   --help  Show this message and exit.
#
# Commands:
#   clean  Remove Papermill metadata from a notebook.
#   fmt    Reformat notebook JSON (adjust indent, trailing newline, filter...
#   run    Run a notebook using Papermill, clean nondeterministic metadata,...
```

#### `juq nb fmt` <a id="juq-nb-fmt"></a>
Format and filter notebook fields:

<!-- `bmdf -- juq nb fmt --help` -->
```bash
juq nb fmt --help
# Usage: juq nb fmt [OPTIONS] [NB_PATH] [OUT_PATH]
#
#   Reformat notebook JSON (adjust indent, trailing newline, filter fields).
#
#   Filter flags:   lowercase (-s, -o, -a, -b, -c, -i, -m) = keep ONLY this
#   field   uppercase (-S, -O, -A, -B, -C, -I, -M) = DROP this field
#
# Options:
#   -a, --attachments / -A, --no-attachments
#                                   Keep only/drop cell attachments
#   -b, --nb-metadata / -B, --no-nb-metadata
#                                   Keep only/drop notebook metadata
#   -c, --execution-count / -C, --no-execution-count
#                                   Keep only/drop execution counts
#   -i, --cell-id / -I, --no-cell-id
#                                   Keep only/drop cell IDs
#   -m, --cell-metadata / -M, --no-cell-metadata
#                                   Keep only/drop cell metadata
#   -o, --outputs / -O, --no-outputs
#                                   Keep only/drop cell outputs
#   -s, --sources / -S, --no-sources
#                                   Keep only/drop cell sources
#   --ensure-ascii                  Octal-escape non-ASCII characters in JSON
#                                   output
#   -w, --in-place                  Modify [NB_PATH] in-place
#   -n, --indent INTEGER            Indentation level for output JSON (default:
#                                   infer from input)
#   --out-path TEXT                 Write to this file instead of stdout
#   -t, --trailing-newline / -T, --no-trailing-newline
#                                   Trailing newline (default: match input)
#   --help                          Show this message and exit.
```

Examples:
```bash
juq nb fmt -s notebook.ipynb          # sources only
juq nb fmt -s -o notebook.ipynb       # sources + outputs only
juq nb fmt -O notebook.ipynb          # drop outputs
juq nb fmt -w -S notebook.ipynb       # in-place, drop sources
```

#### `juq nb run` <a id="juq-nb-run"></a>
Alias for [`juq papermill run`](#juq-papermill).

#### `juq nb clean` <a id="juq-nb-clean"></a>
Alias for [`juq papermill clean`](#juq-papermill).

### `juq cells` <a id="juq-cells"></a>
Slice/Filter cells:

<!-- `bmdf -- juq cells --help` -->
```bash
juq cells --help
# Usage: juq cells [OPTIONS] CELLS_SLICE [NB_PATH] [OUT_PATH]
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

### `juq papermill` <a id="juq-papermill"></a>
Wrapper for Papermill commands. Also available as `juq nb run` / `juq nb clean`.

#### `juq papermill clean`
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
#   -I, --keep-ids / -D, --drop-ids
#                                   Keep or drop cell ids (default: keep).
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

#### `juq papermill run`
<!-- `bmdf -- juq papermill run --help` -->
```bash
juq papermill run --help
# Usage: juq papermill run [OPTIONS] [NB_PATH] [OUT_PATH]
#
#   Run a notebook using Papermill, clean nondeterministic metadata, normalize
#   output streams.
#
# Options:
#   -I, --keep-ids / -D, --drop-ids
#                                   Keep or drop cell ids (default: keep).
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

[juq_py]: https://pypi.org/project/juq_py/
