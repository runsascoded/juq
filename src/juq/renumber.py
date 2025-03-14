from click import option
from nbformat import NotebookNode
from utz import silent, err, decos

from juq.cli import cli, with_nb


def renumber(
    nb: NotebookNode,
    quiet: bool = False,
):
    """Renumber cells (and outputs) with non-null `execution_count` fields (beginning from 1).

    Simulates the executed cells having been executed in order (e.g. to avoid needing to re-run a whole notebook after
    rearranging cells that don't depend on one another).
    """
    log = silent if quiet else err
    nxt_idx = 1
    for cell_idx, cell in enumerate(nb["cells"]):
        found = False
        if cell.get('execution_count') is not None:
            log(f".cells[{cell_idx}].execution_count: {cell['execution_count']} → {nxt_idx}")
            cell['execution_count'] = nxt_idx
            found = True
        for output_idx, output in enumerate(cell.get("outputs", [])):
            if output.get('execution_count') is not None:
                log(f".cells[{cell_idx}].outputs[{output_idx}].execution_count: {output['execution_count']} → {nxt_idx}")
                output['execution_count'] = nxt_idx
                found = True
        if found:
            nxt_idx += 1
    return nb


renumber_cmd = decos(
    cli.command,
    option('-q', '--quiet', is_flag=True, help="Suppress logging info about each `execution_count` update to stderr"),
    with_nb,
)(renumber)
