from utz import err, decos

from juq.cli import with_nb, cli


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
                err(f"Unrecognized keys in prv: {prv_keys - keys}")
            elif cur_keys != keys:
                err(f"Unrecognized keys in cur: {cur_keys - keys}")
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
