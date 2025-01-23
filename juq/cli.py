from __future__ import annotations

import json
from contextlib import nullcontext
from functools import wraps
from inspect import getfullargspec
from os.path import join
from sys import stdin, stdout, stderr
from tempfile import TemporaryDirectory
from typing import Tuple

from click import argument, group, option, UsageError
from papermill.cli import _resolve_type
from utz import decos, recvs


@group()
def cli():
    pass


def with_nb_input(func):
    spec = getfullargspec(func)

    @wraps(func)
    @argument('args', required=False, nargs=-1)
    def wrapper(args, **kwargs):
        if len(args) == 1:
            nb_path = args[0]
        elif len(args) == 2:
            nb_path, out_path = args
            if 'out_path' in kwargs and kwargs['out_path']:
                if out_path != kwargs['out_path']:
                    raise ValueError(f"Specify -o/--out-path xor a 2nd positional arg: {out_path} != {kwargs['out_path']}")
            else:
                kwargs['out_path'] = out_path
        elif len(args) > 2:
            raise UsageError("Too many positional arguments, expected [input-nb [output-nb]]")
        else:
            nb_path = None

        ctx = nullcontext(stdin) if nb_path == '-' or nb_path is None else open(nb_path, 'r')
        with ctx as f:
            nb_str = f.read()
            indent = kwargs.pop('indent', None)
            if indent is None:
                if nb_str.startswith('{'):
                    if nb_str[1] == "\n":
                        idx = 2
                        indent = 0
                        while nb_str[idx] == ' ':
                            idx += 1
                            indent += 1
                    else:
                        indent = None
                else:
                    raise ValueError(f"Cannot infer `indent` from non-JSON input beginning with {nb_str[:30]}")

            trailing_newline = kwargs.pop('trailing_newline', None)
            if trailing_newline is None:
                trailing_newline = nb_str.endswith('\n')
            nb = json.loads(nb_str)
        if recvs(func, 'nb'):
            kwargs['nb'] = nb
        if recvs(func, 'nb_path') or 'nb_path' in spec.kwonlyargs:
            kwargs['nb_path'] = nb_path
        return func(indent=indent, trailing_newline=trailing_newline, **kwargs)
    return wrapper


def with_nb(func):
    @option('-a', '--ensure-ascii', is_flag=True, help='Octal-escape non-ASCII characters in JSON output')
    @option('-i', '--in-place', is_flag=True, help='Modify [NB_PATH] in-place')
    @option('-n', '--indent', type=int, help='Indentation level for the output notebook JSON (default: infer from input)')
    @option('-o', '--out-path', help='Write to this file instead of stdout')
    @option('-t/-T', '--trailing-newline/--no-trailing-newline', default=None, help='Enforce presence or absence of a trailing newline (default: match input)')
    @with_nb_input
    @wraps(func)
    def wrapper(nb_path, *args, ensure_ascii=False, indent=None, trailing_newline=None, **kwargs):
        """Merge consecutive "stream" outputs (e.g. stderr)."""
        in_place = kwargs.get('in_place')
        out_path = kwargs.get('out_path')
        if in_place:
            if out_path:
                raise ValueError("Cannot use `-i` with `-o`")
            if not nb_path or nb_path == '-':
                raise ValueError("Cannot use `-i` without explicit `nb_path`")
            out_path = nb_path

        kwargs['nb_path'] = nb_path
        kwargs = {
            k: v
            for k, v in kwargs.items()
            if recvs(func, k)
        }
        rv = func(*args, **kwargs)
        if isinstance(rv, tuple):
            nb, exc = rv
        elif isinstance(rv, dict):
            nb = rv
            exc = None
        else:
            raise ValueError(f"Unrecognized with_nb return value {type(rv)}: {str(rv)[:100]}")

        out_ctx = nullcontext(stdout) if out_path == '-' or out_path is None else open(out_path, 'w')
        with out_ctx as f:
            json.dump(nb, f, indent=indent, ensure_ascii=ensure_ascii)
            if trailing_newline:
                f.write('\n')

        if exc:
            raise exc

    return wrapper


CELL_TYPE_ABBREVS = {
    'c': 'code',
    'm': 'markdown',
    'md': 'markdown',
    'r': 'raw',
}


@cli.command()
@option('-m/-M', '--metadata/--no-metadata', default=None, help='Explicitly include or exclude each cell\'s "metadata" key. If only `-m` is passed, only the "metadata" value of each cell is printed')
@option('-o/-O', '--outputs/--no-outputs', default=None, help='Explicitly include or exclude each cell\'s "outputs" key. If only `-o` is passed, only the "outputs" value of each cell is printed')
@option('-s/-S', '--source/--no-source', default=None, help='Explicitly include or exclude each cell\'s "source" key. If only `-s` is passed, the source is printed directly (not as JSON)')
@option('-t', '--cell-type', help='Only print cells of this type. Recognizes abbreviations: "c" for "code", {"m","md"} for "markdown", "r" for "raw"')
@argument('cells_slice')
@with_nb_input
def cells(cell_type, cells_slice, nb, **flags):
    """Slice/Filter cells."""
    cells = nb['cells']
    if cell_type:
        if cell_type in CELL_TYPE_ABBREVS:
            cell_type = CELL_TYPE_ABBREVS[cell_type]
        cells = [
            cell
            for cell in cells
            if cell['cell_type'] == cell_type
        ]

    def slice_cell(cell):
        num_flags = sum(1 if v else 0 for v in flags.values())
        if num_flags > 1:
            return {
                k: cell[k]
                for k, v in flags.items()
                if v and k in cell
            }
        elif num_flags == 1:
            for k, v in flags.items():
                if v:
                    if k == 'source':
                        source = cell['source']
                        return ''.join(source) if isinstance(source, list) else source
                    else:
                        return cell[k]
        else:
            return {
                k: cell[k]
                for k, v in cell.items()
                if flags.get(k)is not False
            }

    pcs = cells_slice.split(':')
    if len(pcs) == 1:
        cell = cells[int(pcs[0])]
        cell = slice_cell(cell)
        obj = cell
    elif len(pcs) == 2:
        cells = cells[slice(*map(lambda x: int(x.strip()) if x.strip() else None, pcs))]
        cells = [
            slice_cell(cell)
            for cell in cells
        ]
        obj = cells
    else:
        raise ValueError(f"Unrecognized <cells slice>: {cells_slice}")

    if isinstance(obj, str):
        print(obj)
    else:
        print(json.dumps(obj, indent=2))


def merge_cell_outputs(cell):
    if 'outputs' not in cell:
        return cell
    outputs = cell['outputs']
    new = []
    prv = None
    for cur in outputs:
        if (
                prv and
                prv['output_type'] == "stream" and
                cur['output_type'] == "stream" and
                prv.get('name') and
                prv.get('name') == cur.get('name')
        ):
            prv_keys = set(prv.keys())
            cur_keys = set(cur.keys())
            keys = { 'output_type', 'name', 'text' }
            if prv_keys != keys:
                stderr.write(f"Unrecognized keys in prv: {prv_keys - keys}\n")
            elif cur_keys != keys:
                stderr.write(f"Unrecognized keys in cur: {cur_keys - keys}\n")
            else:
                prv['text'] += cur['text']
                prv = cur
                continue
        new.append(cur)
        prv = cur
    cell['outputs'] = new
    return cell


def merge_outputs(nb):
    """Merge consecutive "stream" outputs (e.g. stderr)."""
    nb['cells'] = [
        merge_cell_outputs(cell)
        for cell in nb['cells']
    ]
    return nb


merge_outputs_cmd = decos(
    cli.command('merge-outputs'),
    with_nb,
)(merge_outputs)


@cli.group
def papermill():
    """Wrapper for Papermill commands (`clean`, `run`)."""
    pass


def papermill_clean_cell(
    cell,
    keep_ids: bool = False,
    keep_tags: bool | None = False,
):
    if not keep_ids and 'id' in cell:
        del cell['id']
    if 'metadata' in cell:
        metadata = cell['metadata']
        for k in [ 'papermill', 'execution', 'widgets' ]:
            if k in metadata:
                del metadata[k]
        if keep_tags is True:
            if 'tags' not in metadata:
                metadata['tags'] = []
        elif keep_tags is False:
            if 'tags' in metadata and not metadata['tags']:
                del metadata['tags']
    return cell


def papermill_clean(
    nb,
    keep_ids: bool = False,
    keep_tags: bool | None = False,
):
    """Remove Papermill metadata from a notebook.

    Removes `.metadata.papermill` and `.cells[*].metadata.{papermill,execution,widgets}`.
    """
    nb['cells'] = [
        papermill_clean_cell(
            cell,
            keep_ids=keep_ids,
            keep_tags=keep_tags,
        )
        for cell in nb['cells']
    ]
    metadata = nb['metadata']
    if 'papermill' in metadata:
        del metadata['papermill']
    return nb


nb_opts = decos(
    option('-I', '--keep-ids', is_flag=True, help='Keep cell ids'),
    option('-k', '--keep-tags', is_flag=True, default=None, help='When a cell\'s `tags` array is empty, enforce its presence or absence in the output'),
)

papermill_clean_cmd = decos(
    papermill.command('clean'),
    nb_opts,
    with_nb,
)(papermill_clean)


def papermill_run(
    nb_path,
    keep_ids: bool = False,
    keep_tags: bool | None = None,
    parameter_strs: Tuple[str, ...] = (),
    request_save_on_cell_execute: bool | None = None,
    autosave_cell_every: int | None = None,
):
    """Run a notebook using Papermill, clean nondeterministic metadata, normalize output streams."""
    from papermill import PapermillExecutionError, execute_notebook

    parameters = {}
    for param_str in parameter_strs:
        pcs = param_str.split('=', 1)
        if len(pcs) != 2:
            raise ValueError(f"Unrecognized parameter string: {param_str}")
        k, v = pcs
        parameters[k] = _resolve_type(v)

    exc = None
    with TemporaryDirectory() as tmpdir:
        tmp_out = join(tmpdir, 'out.ipynb')
        try:
            execute_notebook(
                nb_path, tmp_out,
                parameters=parameters,
                request_save_on_cell_execute=request_save_on_cell_execute,
                **({} if autosave_cell_every is None else dict(autosave_cell_every=autosave_cell_every)),
            )
        except PapermillExecutionError as e:
            exc = e

        with open(tmp_out, 'r') as f:
            nb = json.load(f)

    if keep_tags is None:
        with open(nb_path, 'r') as f:
            nb0 = json.load(f)
        cells0 = nb0['cells']
        cells1 = nb['cells']

        idx1 = 0

        def skip_injected_param_cells():
            """Skip ``idx1`` past any "injected-parameters" or "error" cells Papermill may have inserted."""
            nonlocal idx1
            while True:
                cell1 = cells1[idx1]
                md1 = cell1.get('metadata', {})
                tags1 = md1.get('tags')
                if not tags1 or not {"papermill-error-cell-tag", 'injected-parameters'} & set(tags1):
                    return cell1, md1, tags1
                idx1 += 1

        for idx0, cell0 in enumerate(cells0):
            md0 = cell0['metadata']
            cell1, md1, tags1 = skip_injected_param_cells()
            source0 = cell0.get('source')
            source1 = cell1.get('source')
            if source0 != source1:
                raise ValueError(f"Cell {idx0=}: {source0=} != {source1=}")
            if 'tags' not in md0 and tags1 == []:
                del md1['tags']
            idx1 += 1
        try:
            skip_injected_param_cells()
        except IndexError:
            pass
        if idx1 != len(cells1):
            raise ValueError(f'"After" notebook has {len(cells1) - idx1} extra cells: {json.dump(cells1[idx1:], stdout)}')

    nb = papermill_clean(nb, keep_ids=keep_ids, keep_tags=keep_tags)
    nb = merge_outputs(nb)
    return nb, exc


papermill_run_cmd = decos(
    papermill.command('run'),
    nb_opts,
    option('-p', '--parameter', 'parameter_strs', multiple=True, help='"<k>=<v>" variable to set, while executing the notebook'),
    option('-s', '--request-save-on-cell-execute', is_flag=True, default=None, help="Request save notebook after each cell execution"),
    option('-S', '--autosave-cell-every', type=int, help="How often in seconds to autosave the notebook during long cell executions (0 to disable)"),
    with_nb,
)(papermill_run)


if __name__ == '__main__':
    cli()
