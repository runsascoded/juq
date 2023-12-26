import json
from contextlib import contextmanager
from fileinput import FileInput
from sys import stdin

import click
import nbformat


@click.group()
def cli():
    pass


@contextmanager
def identity(obj):
    yield obj


@cli.command()
@click.option('-m/-M', '--metadata/--no-metadata', is_flag=True)
@click.option('-o/-O', '--outputs/--no-outputs', default=None)
@click.option('-s/-S', '--source/--no-source', default=None)
@click.option('-t', '--cell-type')
@click.argument('cells_slice')
@click.argument('nb_path', required=False)
def cells(cell_type, cells_slice, nb_path, **flags):
    ctx = identity(stdin) if nb_path == '-' or nb_path is None else open(nb_path, 'r')
    with ctx as f:
        # nb = nbformat.read(f, as_version=4)
        nb = json.load(f)
        cells = nb['cells']

    if cell_type:
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


if __name__ == '__main__':
    cli()
