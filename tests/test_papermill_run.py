import json
from os.path import join
from tempfile import TemporaryDirectory

from juq.papermill.run import papermill_run_cmd
from tests.test_papermill_clean import TEST_DIR


def test_mixed_tags():
    name = "mixed-tags.ipynb"
    before_path = join(TEST_DIR, name)
    with open(before_path, 'r') as f:
        before = json.load(f)
    with TemporaryDirectory() as tmpdir:
        after_path = join(tmpdir, name)
        papermill_run_cmd.callback((before_path,), out_path=after_path)
        with open(after_path, 'r') as f:
            after = json.load(f)

    assert after == before


def test_mixed_tags_params():
    before_path = join(TEST_DIR, "mixed-tags-params.ipynb")
    name = "mixed-tags-params-222.ipynb"
    expected_path = join(TEST_DIR, name)
    with open(expected_path, 'r') as f:
        expected = json.load(f)
    with TemporaryDirectory() as tmpdir:
        after_path = join(tmpdir, name)
        papermill_run_cmd.callback((before_path,), parameter_strs=("num=222",), out_path=after_path)
        with open(after_path, 'r') as f:
            actual = json.load(f)

    assert actual == expected
