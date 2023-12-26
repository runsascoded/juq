import json
from contextlib import contextmanager
from functools import wraps
from inspect import getfullargspec
from sys import stdin, stdout, stderr

import click


@click.group()
def cli():
    pass


@contextmanager
def identity(obj):
    yield obj


def with_nb(func):
    spec = getfullargspec(func)

    @wraps(func)
    @click.argument('nb_path', required=False)
    def wrapper(nb_path, *args, **kwargs):
        ctx = identity(stdin) if nb_path == '-' or nb_path is None else open(nb_path, 'r')
        with ctx as f:
            # nb = nbformat.read(f, as_version=4)
            nb = json.load(f)
        # ctx = identity(stdin) if nb_path == '-' else open(nb_path, 'r')
        # with ctx as f:
        #     nb = nbformat.read(f, as_version=4)
        if 'nb_path' in spec.args:
            kwargs['nb_path'] = nb_path
        func(*args, nb=nb, **kwargs)
        # with ctx as f:
        #     nbformat.write(nb, f)
    return wrapper


CELL_TYPE_ABBREVS = {
    'c': 'code',
    'm': 'markdown',
    'md': 'markdown',
    'r': 'raw',
}


@cli.command()
@click.option('-m/-M', '--metadata/--no-metadata', default=None, help='Explicitly include or exclude each cell\'s "metadata" key. If only `-m` is passed, only the "metadata" value of each cell is printed')
@click.option('-o/-O', '--outputs/--no-outputs', default=None, help='Explicitly include or exclude each cell\'s "outputs" key. If only `-o` is passed, only the "outputs" value of each cell is printed')
@click.option('-s/-S', '--source/--no-source', default=None, help='Explicitly include or exclude each cell\'s "source" key. If only `-s` is passed, the source is printed directly (not as JSON)')
@click.option('-t', '--cell-type', help='Only print cells of this type. Recognizes abbreviations: "c" for "code", {"m","md"} for "markdown", "r" for "raw"')
@click.argument('cells_slice')
@with_nb
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


@cli.command('merge-outputs')
@click.option('-i', '--in-place', is_flag=True, help='Modify [NB_PATH] in-place')
@click.option('-o', '--out-path', help='Write to this file instead of stdout')
@with_nb
def merge_outputs(nb, nb_path, in_place, out_path):
    """Merge consecutive "stream" outputs (e.g. stderr)."""
    if in_place:
        if out_path:
            raise ValueError("Cannot use `-i` with `-o`")
        if not nb_path or nb_path == '-':
            raise ValueError("Cannot use `-i` without explicit `nb_path`")
        out_path = nb_path
    nb['cells'] = [
        merge_cell_outputs(cell)
        for cell in nb['cells']
    ]

    ctx = identity(stdout) if out_path == '-' or out_path is None else open(out_path, 'w')
    with ctx as f:
        json.dump(nb, f, indent=2)


if __name__ == '__main__':
    cli()
