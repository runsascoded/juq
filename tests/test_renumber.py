import json
from os.path import join, basename
from tempfile import TemporaryDirectory

from juq.renumber import renumber_cmd
from tests.utils import TEST_DIR


def test_renumber_execution_counts():
    name = 'test-renumber'
    in_path = join(TEST_DIR, f"{name}.ipynb")
    expected_path = join(TEST_DIR, f"{name}-out.ipynb")
    with TemporaryDirectory() as tmpdir:
        out_path = join(tmpdir, basename(expected_path))
        renumber_cmd.callback(in_path, out_path)
        with open(out_path, 'r') as f:
            actual = json.load(f)
    # with open(expected_path, 'w') as f:
    #     json.dump(actual, f, indent=1)
    with open(expected_path, 'r') as f:
        expected = json.load(f)
    assert actual == expected
