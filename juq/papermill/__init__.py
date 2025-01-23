from click import option
from utz import decos

from juq.cli import cli


@cli.group
def papermill():
    """Wrapper for Papermill commands (`clean`, `run`)."""
    pass


nb_opts = decos(
    option('-I', '--keep-ids', is_flag=True, help='Keep cell ids'),
    option('-k', '--keep-tags', is_flag=True, default=None, help='When a cell\'s `tags` array is empty, enforce its presence or absence in the output'),
)
