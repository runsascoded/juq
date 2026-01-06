import re
import sys
from copy import deepcopy
from os.path import join, dirname

TEST_DIR = join(dirname(__file__), "files")
MERGE_OUTPUTS_DIR = join(TEST_DIR, "merge-outputs")

PYTHON_VERSION = ".".join(map(str, sys.version_info[:3]))

# ANSI escape code pattern
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def strip_ansi(s):
    """Strip ANSI escape codes from a string."""
    return ANSI_ESCAPE.sub('', s)


def normalize_nb(nb, *, keep_ids=False):
    """Normalize notebook for comparison.

    - Normalizes language_info.version to current Python
    - Drops cell IDs by default (since papermill generates new IDs for injected cells)
    - Strips ANSI escape codes from outputs (vary by Python version)
    """
    nb = deepcopy(nb)

    # Normalize Python version
    lang_info = nb.get('metadata', {}).get('language_info', {})
    if 'version' in lang_info:
        lang_info['version'] = PYTHON_VERSION

    # Drop cell IDs unless explicitly keeping them
    if not keep_ids:
        for cell in nb.get('cells', []):
            cell.pop('id', None)

    # Strip ANSI codes from outputs (traceback colors vary by Python version)
    for cell in nb.get('cells', []):
        for output in cell.get('outputs', []):
            if 'text' in output:
                if isinstance(output['text'], list):
                    output['text'] = [strip_ansi(line) for line in output['text']]
                else:
                    output['text'] = strip_ansi(output['text'])
            if 'traceback' in output:
                output['traceback'] = [strip_ansi(line) for line in output['traceback']]

    return nb
