from copy import deepcopy

from utz import err, decos

from juq.cli import with_nb, cli


def merge_cell_outputs(cell):
    if 'outputs' not in cell:
        return cell
    outputs = cell['outputs']
    new = []
    i = 0
    n = len(outputs)
    while i < n:
        cur = deepcopy(outputs[i])
        if cur['output_type'] == "stream" and cur.get('name'):
            name = cur['name']
            while True:
                i += 1
                if i == n:
                    break
                nxt = outputs[i]
                if nxt['output_type'] == "stream" and nxt.get('name') == name:
                    cur['text'] += nxt['text']
                else:
                    break
        else:
            i += 1
        new.append(cur)
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
