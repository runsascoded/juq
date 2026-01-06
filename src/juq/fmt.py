from utz import decos

from juq.cli import with_nb, cli


def fmt(nb):
    """Reformat notebook JSON (adjust indent, trailing newline, etc.)."""
    return nb


fmt_cmd = decos(
    cli.command('fmt'),
    with_nb,
)(fmt)
