import json
from subprocess import check_output


def run_fmt(*args):
    output = check_output(['juq', 'nb', 'fmt', *args])
    return json.loads(output)


def test_fmt_no_filter():
    """No filter flags = passthrough."""
    nb = run_fmt('tests/files/mixed-tags.ipynb')
    cell = nb['cells'][0]
    assert 'source' in cell
    assert 'outputs' in cell
    assert 'metadata' in cell
    assert 'execution_count' in cell
    assert 'id' in cell


def test_fmt_sources_only():
    """-s keeps only sources."""
    nb = run_fmt('-s', 'tests/files/mixed-tags.ipynb')
    cell = nb['cells'][0]
    assert 'source' in cell
    assert 'outputs' not in cell
    assert 'metadata' not in cell
    assert 'execution_count' not in cell
    assert 'id' not in cell
    assert nb['metadata'] == {}


def test_fmt_drop_sources():
    """-S drops sources, keeps everything else."""
    nb = run_fmt('-S', 'tests/files/mixed-tags.ipynb')
    cell = nb['cells'][0]
    assert 'source' not in cell
    assert 'outputs' in cell
    assert 'metadata' in cell
    assert 'execution_count' in cell
    assert 'id' in cell


def test_fmt_multiple_includes():
    """-s -m keeps sources + metadata only."""
    nb = run_fmt('-s', '-m', 'tests/files/mixed-tags.ipynb')
    cell = nb['cells'][0]
    assert 'source' in cell
    assert 'metadata' in cell
    assert 'outputs' not in cell
    assert 'execution_count' not in cell
    assert 'id' not in cell


def test_fmt_multiple_excludes():
    """-S -C drops sources and execution_count."""
    nb = run_fmt('-S', '-C', 'tests/files/mixed-tags.ipynb')
    cell = nb['cells'][0]
    assert 'source' not in cell
    assert 'execution_count' not in cell
    assert 'outputs' in cell
    assert 'metadata' in cell
    assert 'id' in cell


def test_fmt_drop_outputs():
    """-O drops outputs."""
    nb = run_fmt('-O', 'tests/files/mixed-tags.ipynb')
    cell = nb['cells'][0]
    assert 'source' in cell
    assert 'outputs' not in cell
    assert 'metadata' in cell


def test_fmt_sources_and_outputs():
    """-s -o keeps sources + outputs."""
    nb = run_fmt('-s', '-o', 'tests/files/mixed-tags.ipynb')
    cell = nb['cells'][0]
    assert 'source' in cell
    assert 'outputs' in cell
    assert 'metadata' not in cell
    assert 'execution_count' not in cell
    assert 'id' not in cell
