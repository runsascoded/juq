from __future__ import annotations

import json
from os.path import join, basename
from tempfile import TemporaryDirectory

from juq.papermill.run import papermill_run_cmd
from tests.test_papermill_clean import TEST_DIR


def check(
    in_name: str,
    expected_name: str | None = None,
    **kwargs,
):
    in_path = join(TEST_DIR, in_name)
    if expected_name is None:
        expected_name = in_name
    expected_path = join(TEST_DIR, expected_name)
    name = basename(expected_path)
    with TemporaryDirectory() as tmpdir:
        out_path = join(tmpdir, name)
        papermill_run_cmd.callback(in_path, out_path, **kwargs)
        with open(out_path, 'r') as f:
            actual = json.load(f)
    with open(expected_path, 'r') as f:
        expected = json.load(f)
    assert actual == expected


def test_mixed_tags():
    check("mixed-tags.ipynb")


def test_mixed_tags_params():
    check(
        "mixed-tags-params.ipynb",
        "mixed-tags-params-222.ipynb",
        parameter_strs=("num=222",),
    )


def test_run_previously_run_nb():
    check(
        "mixed-tags-params-222.ipynb",
        "mixed-tags-params-333.ipynb",
        parameter_strs=("num=333",),
    )


def test_mixed_tags_keep():
    check(
        "mixed-tags.ipynb",
        "mixed-tags-keep.ipynb",
        keep_tags=True,
    )


def test_mixed_tags_drop():
    check(
        "mixed-tags.ipynb",
        "mixed-tags-drop.ipynb",
        keep_tags=False,
    )
