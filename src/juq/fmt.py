from click import option
from utz import decos

from juq.cli import with_nb, cli


def filter_cell(cell, *, sources=True, outputs=True, metadata=True, execution_count=True, cell_id=True, attachments=True):
    """Filter cell fields based on flags."""
    result = {'cell_type': cell['cell_type']}
    if sources and 'source' in cell:
        result['source'] = cell['source']
    if outputs and 'outputs' in cell:
        result['outputs'] = cell['outputs']
    if metadata and 'metadata' in cell:
        result['metadata'] = cell['metadata']
    if execution_count and 'execution_count' in cell:
        result['execution_count'] = cell['execution_count']
    if cell_id and 'id' in cell:
        result['id'] = cell['id']
    if attachments and 'attachments' in cell:
        result['attachments'] = cell['attachments']
    return result


def fmt(
    nb,
    sources=None,
    outputs=None,
    cell_metadata=None,
    execution_count=None,
    cell_id=None,
    attachments=None,
    nb_metadata=None,
):
    """Reformat notebook JSON (adjust indent, trailing newline, filter fields).

    Filter flags: lowercase (-s, -b, -c, -I, -m) = keep ONLY this field
                  uppercase (-S, -B, -C, -D, -M) = DROP this field
                  --outputs, --attachments = keep only; --no-outputs, --no-attachments = drop
    """
    # Check for "only" mode: if exactly one field is explicitly True, keep only that
    explicit_true = [
        ('sources', sources),
        ('outputs', outputs),
        ('attachments', attachments),
        ('nb_metadata', nb_metadata),
        ('cell_metadata', cell_metadata),
        ('execution_count', execution_count),
        ('cell_id', cell_id),
    ]
    only_fields = [name for name, val in explicit_true if val is True]

    if only_fields:
        # "Only" mode: keep only explicitly requested fields, drop the rest
        keep_sources = 'sources' in only_fields
        keep_outputs = 'outputs' in only_fields
        keep_attachments = 'attachments' in only_fields
        keep_nb_metadata = 'nb_metadata' in only_fields
        keep_metadata = 'cell_metadata' in only_fields
        keep_exec_count = 'execution_count' in only_fields
        keep_cell_id = 'cell_id' in only_fields
    else:
        # "Drop" mode: keep everything except explicitly dropped fields
        keep_sources = sources is not False
        keep_outputs = outputs is not False
        keep_attachments = attachments is not False
        keep_nb_metadata = nb_metadata is not False
        keep_metadata = cell_metadata is not False
        keep_exec_count = execution_count is not False
        keep_cell_id = cell_id is not False

    # Filter cells
    nb['cells'] = [
        filter_cell(
            cell,
            sources=keep_sources,
            outputs=keep_outputs,
            metadata=keep_metadata,
            execution_count=keep_exec_count,
            cell_id=keep_cell_id,
            attachments=keep_attachments,
        )
        for cell in nb['cells']
    ]

    # Filter notebook metadata
    if not keep_nb_metadata:
        nb['metadata'] = {}

    return nb


fmt_cmd = decos(
    cli.command('fmt'),
    option('--attachments/--no-attachments', 'attachments', default=None, help='Keep only/drop cell attachments'),
    option('-b/-B', '--nb-metadata/--no-nb-metadata', default=None, help='Keep only/drop notebook metadata'),
    option('-c/-C', '--execution-count/--no-execution-count', default=None, help='Keep only/drop execution counts'),
    option('-I/-D', '--cell-id/--no-cell-id', default=None, help='Keep only/drop cell IDs'),
    option('-m/-M', '--cell-metadata/--no-cell-metadata', default=None, help='Keep only/drop cell metadata'),
    option('--outputs/--no-outputs', 'outputs', default=None, help='Keep only/drop cell outputs'),
    option('-s/-S', '--sources/--no-sources', default=None, help='Keep only/drop cell sources'),
    with_nb,
)(fmt)
