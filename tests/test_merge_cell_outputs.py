import json
from os import path
from tempfile import TemporaryDirectory

from juq.merge_outputs import merge_outputs_cmd
from tests.test_papermill_clean import MERGE_OUTPUTS_DIR


def test_merge_cell_outputs():
    nb_path = path.join(MERGE_OUTPUTS_DIR, "split-outputs.ipynb")
    out_name = "merged-outputs.ipynb"
    expected_path = path.join(MERGE_OUTPUTS_DIR, out_name)
    with TemporaryDirectory() as tmpdir:
        actual_path = path.join(tmpdir, out_name)
        merge_outputs_cmd.callback(nb_path, actual_path)
        with open(expected_path, 'r') as f:
            expected_nb = json.load(f)
        with open(actual_path, 'r') as f:
            actual_nb = json.load(f)
    assert expected_nb == actual_nb
