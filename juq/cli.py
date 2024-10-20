import json
from contextlib import nullcontext
from functools import wraps
from inspect import getfullargspec
from subprocess import check_output
from sys import stdin, stdout, stderr

from click import argument, group, option


@group()
def cli():
    pass


def with_nb_input(func):
    spec = getfullargspec(func)

    @wraps(func)
    @argument('nb_path', required=False)
    def wrapper(nb_path, *args, **kwargs):
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
        if 'nb_path' in spec.args or 'nb_path' in spec.kwonlyargs:
            kwargs['nb_path'] = nb_path
        return func(*args, nb=nb, indent=indent, trailing_newline=trailing_newline, **kwargs)
    return wrapper


def with_nb(func):
    spec = getfullargspec(func)

    @wraps(func)
    @option('-i', '--in-place', is_flag=True, help='Modify [NB_PATH] in-place')
    @option('-n', '--indent', type=int, help='Indentation level for the output notebook JSON (default: infer from input)')
    @option('-o', '--out-path', help='Write to this file instead of stdout')
    @option('-t/-T', '--trailing-newline/--no-trailing-newline', default=None, help='Enforce presence or absence of a trailing newline (default: match input)')
    @with_nb_input
    def wrapper(*args, nb_path, indent, trailing_newline, **kwargs):
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
            if k in spec.args
        }
        nb = func(*args, **kwargs)

        out_ctx = nullcontext(stdout) if out_path == '-' or out_path is None else open(out_path, 'w')
        with out_ctx as f:
            json.dump(nb, f, indent=indent)
            if trailing_newline:
                f.write('\n')

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


merge_outputs_cmd = cli.command('merge-outputs')(with_nb(merge_outputs))


@cli.group
def papermill():
    """Wrapper for Papermill commands (`clean`, `run`)."""
    pass


def papermill_clean_cell(cell):
    if 'id' in cell:
        del cell['id']
    if 'metadata' in cell:
        metadata = cell['metadata']
        for k in [ 'papermill', 'execution', 'widgets' ]:
            if k in metadata:
                del metadata[k]
    return cell


def papermill_clean(nb):
    """Remove Papermill metadata from a notebook.

    Removes `.metadata.papermill` and `.cells[*].metadata.{papermill,execution,widgets}`.
    """
    nb['cells'] = [
        papermill_clean_cell(cell)
        for cell in nb['cells']
    ]
    metadata = nb['metadata']
    if 'papermill' in metadata:
        del metadata['papermill']
    return nb


papermill_clean_cmd = papermill.command('clean')(with_nb(papermill_clean))


@papermill.command('run')
@option('-p', '--parameter', 'parameter_strs', multiple=True, help='"<k>=<v>" variable to set, while executing the notebook')
@with_nb
def papermill_run(nb, parameter_strs):
    """Run a notebook using Papermill, clean nondeterministic metadata, normalize output streams."""
    param_args = []
    for param_str in parameter_strs:
        pcs = param_str.split('=', 1)
        if len(pcs) != 2:
            raise ValueError(f"Unrecognized parameter string: {param_str}")
        param_args.extend(['-p', pcs[0], pcs[1]])
    output = check_output(['papermill', *param_args], input=json.dumps(nb).encode())
    nb = json.loads(output)
    nb = papermill_clean(nb)
    nb = merge_outputs(nb)
    return nb


if __name__ == '__main__':
    cli()
