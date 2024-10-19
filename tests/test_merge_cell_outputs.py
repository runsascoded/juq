import json
from os import path
from os.path import dirname
from tempfile import TemporaryDirectory

from juq.cli import merge_outputs_cmd

TEST_DIR = path.join(dirname(__file__), "files", "merge-outputs")


def test_merge_cell_outputs():
    nb_path = path.join(TEST_DIR, "split-outputs.ipynb")
    out_name = "merged-outputs.ipynb"
    expected_path = path.join(TEST_DIR, out_name)
    with TemporaryDirectory() as tmpdir:
        actual_path = path.join(tmpdir, out_name)
        merge_outputs_cmd.callback(nb_path=nb_path, out_path=actual_path)
        with open(expected_path, 'r') as f:
            expected_nb = json.load(f)
        with open(actual_path, 'r') as f:
            actual_nb = json.load(f)
    assert expected_nb == actual_nb
