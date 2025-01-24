from __future__ import annotations

import json
from os.path import join
from sys import stdout
from tempfile import TemporaryDirectory
from typing import Tuple

from click import option
from papermill.cli import _resolve_type
from utz import decos, env

from juq.cli import with_nb
from juq.merge_outputs import merge_outputs
from juq.papermill import nb_opts, papermill
from juq.papermill.clean import papermill_clean


INJECTED_TAGS = { "papermill-error-cell-tag", 'injected-parameters' }


class AlignmentError(ValueError):
    """Indicates a failure to align a generated notebook against its input.

    Papermill always adds empty ``.cells[].metadata.tags`` arrays, which we try to undo when -k/--keep-tags is not
    specified. Output notebooks may have "injected-parameters" cells inserted by Papermill, so we attempt to align the
    input and output notebooks, to mirror presence/absence of ``tags``. ``AlignmentError`` is raised when this process
    fails (e.g. because there appear to be additional, unrecognized cells added to the "output" notebook).
    """
    pass


def harmonize_empty_tags(cells0, cells1, exc):
    """When -k/--keep-tags is not specified, remove empty ``.cells[].metadata.tags`` arrays added by Papermill."""
    idx1 = 0

    def skip_injected_param_cells():
        """Skip ``idx1`` past any "injected-parameters" or "error" cells Papermill may have inserted."""
        nonlocal idx1
        while True:
            cell1 = cells1[idx1]
            md1 = cell1.get('metadata', {})
            tags1 = md1.get('tags')
            if not tags1 or not INJECTED_TAGS & set(tags1):
                return cell1, md1, tags1
            idx1 += 1

    try:
        for idx0, cell0 in enumerate(cells0):
            md0 = cell0['metadata']
            tags0 = md0.get('tags')
            if tags0 and len(tags0) == 1 and tags0[0] in INJECTED_TAGS:
                cell1 = cells1[idx1]
                md1 = cell1.get('metadata', {})
                tags1 = md1.get('tags')
                if tags0 != tags1:
                    raise AlignmentError(f"{tags0=} != {tags1=}")
            else:
                cell1, md1, tags1 = skip_injected_param_cells()
                source0 = cell0.get('source')
                source1 = cell1.get('source')
                if source0 != source1:
                    raise AlignmentError(f"Cell {idx0=}: {source0=} != {source1=}")
                if 'tags' not in md0 and tags1 == []:
                    del md1['tags']
            idx1 += 1
        try:
            skip_injected_param_cells()
        except IndexError:
            pass
        if idx1 != len(cells1):
            raise AlignmentError(f'"After" notebook has {len(cells1) - idx1} extra cells: {json.dump(cells1[idx1:], stdout)}')
    except AlignmentError as align_exc:
        if exc:
            align_exc.__cause__ = exc
        exc = align_exc
    return exc


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
            with env(PAPERMILL='1'):
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
        exc = harmonize_empty_tags(cells0, cells1, exc)

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
