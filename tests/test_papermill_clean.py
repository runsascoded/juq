import json
from os import path
from os.path import dirname
from tempfile import TemporaryDirectory
from papermill import execute_notebook
from juq.cli import papermill_clean

TEST_DIR = path.join(dirname(__file__), "files", "merge-outputs")


def test_papermill_clean():
    nb_path = path.join(TEST_DIR, "merged-outputs.ipynb")
    with TemporaryDirectory() as tmpdir:
        post_papermill_path = path.join(tmpdir, 'post-papermill.ipynb')
        execute_notebook(nb_path, post_papermill_path)
        with open(post_papermill_path, 'r') as f:
            post_papermill = json.load(f)
        assert 'papermill' in post_papermill['cells'][0]['metadata']
        assert 'papermill' in post_papermill['metadata']

        cleaned_path = path.join(tmpdir, 'cleaned.ipynb')
        papermill_clean.callback(nb_path=post_papermill_path, out_path=cleaned_path)
        with open(cleaned_path, 'r') as f:
            cleaned_nb = json.load(f)
        split_outputs_nb_path = path.join(TEST_DIR, "split-outputs.ipynb")
        with open(split_outputs_nb_path, 'r') as f:
            split_outputs_nb = json.load(f)
    assert cleaned_nb == split_outputs_nb
