from __future__ import annotations

from utz import decos

from juq.cli import with_nb
from juq.papermill import papermill, nb_opts


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


papermill_clean_cmd = decos(
    papermill.command('clean'),
    nb_opts,
    with_nb,
)(papermill_clean)
