import json
from os.path import join
from subprocess import check_call, CalledProcessError
from tempfile import TemporaryDirectory

from papermill import execute_notebook, PapermillExecutionError
from pytest import raises
from utz import env

from juq.papermill.clean import papermill_clean_cmd
from juq.papermill.run import papermill_run_cmd
from tests.utils import MERGE_OUTPUTS_DIR, TEST_DIR, normalize_nb


def test_papermill_clean():
    nb_path = join(MERGE_OUTPUTS_DIR, "merged-outputs.ipynb")
    with TemporaryDirectory() as tmpdir:
        post_papermill_path = join(tmpdir, 'post-papermill.ipynb')
        execute_notebook(nb_path, post_papermill_path)
        with open(post_papermill_path, 'r') as f:
            post_papermill = json.load(f)
        assert 'papermill' in post_papermill['cells'][0]['metadata']
        assert 'papermill' in post_papermill['metadata']

        cleaned_path = join(tmpdir, 'cleaned.ipynb')
        papermill_clean_cmd.callback(post_papermill_path, cleaned_path)
        with open(cleaned_path, 'r') as f:
            actual = json.load(f)
        split_outputs_nb_path = join(MERGE_OUTPUTS_DIR, "split-outputs.ipynb")
        with open(split_outputs_nb_path, 'r') as f:
            expected = json.load(f)
    assert normalize_nb(actual) == normalize_nb(expected)


def test_papermill_error():
    nb_path = join(TEST_DIR, "test-err.ipynb")
    with TemporaryDirectory() as tmpdir, env(NO_COLOR="1"):
        out_path1 = join(tmpdir, 'out1.ipynb')
        with raises(PapermillExecutionError):
            papermill_run_cmd.callback(
                nb_path, out_path1,
                keep_ids=False,
                keep_tags=None,
                parameter_strs=(),
                request_save_on_cell_execute=False,
                autosave_cell_every=False,
            )

        with open(join(TEST_DIR, "test-err-out.ipynb"), 'r') as f:
            expected = json.load(f)

        with open(out_path1, 'r') as f:
            actual1 = json.load(f)
        assert normalize_nb(actual1) == normalize_nb(expected)

        out_path2 = join(tmpdir, 'out2.ipynb')
        with raises(CalledProcessError):
            check_call(['juq', 'papermill', 'run', '-D', '-n1', nb_path, out_path2])

        with open(out_path2, 'r') as f:
            actual2 = json.load(f)
        assert normalize_nb(actual2) == normalize_nb(expected)
