import json

from click import argument, option

from juq.cli import with_nb_input, cli

CELL_TYPE_ABBREVS = {
    'c': 'code',
    'm': 'markdown',
    'md': 'markdown',
    'r': 'raw',
}


@cli.command
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
