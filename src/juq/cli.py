from __future__ import annotations

import json
from contextlib import nullcontext
from functools import wraps
from inspect import getfullargspec
from os.path import exists
from sys import stdin, stdout

from click import argument, group, option, pass_context
from utz import recvs, call


@group()
def cli():
    pass


def infer_nb_indent(nb_str: str) -> int | None:
    """Infer indentation level from notebook JSON string."""
    if nb_str.startswith('{'):
        if len(nb_str) > 1 and nb_str[1] == "\n":
            idx = 2
            indent = 0
            while idx < len(nb_str) and nb_str[idx] == ' ':
                idx += 1
                indent += 1
            return indent
        else:
            return None
    else:
        raise ValueError(f"Cannot infer `indent` from non-JSON input beginning with {nb_str[:30]}")


def infer_nb_trailing_newline(nb_str: str) -> bool:
    """Infer whether notebook string has trailing newline."""
    return nb_str.endswith('\n')


def write_nb(
    nb: dict,
    path: str,
    indent: int | None = None,
    ensure_ascii: bool = False,
    trailing_newline: bool | None = None,
):
    """Write a notebook dict to a file.

    If indent is None and the file exists, infer indent from existing file.
    If trailing_newline is None and the file exists, infer from existing file.
    """
    if (indent is None or trailing_newline is None) and exists(path):
        with open(path) as f:
            existing = f.read()
        if indent is None:
            indent = infer_nb_indent(existing)
            if indent is None:
                indent = 1
        if trailing_newline is None:
            trailing_newline = infer_nb_trailing_newline(existing)
    else:
        if indent is None:
            indent = 1
        if trailing_newline is None:
            trailing_newline = True

    with open(path, 'w') as f:
        json.dump(nb, f, indent=indent, ensure_ascii=ensure_ascii)
        if trailing_newline:
            f.write('\n')


def with_nb_input(func):
    spec = getfullargspec(func)

    @wraps(func)
    @argument('nb_path', required=False)
    @argument('out_path_arg', required=False, metavar='[OUT_PATH]')
    def wrapper(
        nb_path: str | None = None,
        out_path_arg: str | None = None,
        **kwargs,
    ):
        # Merge positional out_path_arg with -o/--out-path option
        out_path_opt = kwargs.pop('out_path', None)
        if out_path_arg and out_path_opt:
            raise ValueError(f"Specify -o/--out-path xor a 2nd positional arg, not both: {out_path_arg} != {out_path_opt}")
        out_path = out_path_arg or out_path_opt

        ctx = nullcontext(stdin) if nb_path == '-' or nb_path is None else open(nb_path, 'r')
        with ctx as f:
            nb_str = f.read()
            indent = kwargs.pop('indent', None)
            if indent is None:
                indent = infer_nb_indent(nb_str)

            trailing_newline = kwargs.pop('trailing_newline', None)
            if trailing_newline is None:
                trailing_newline = infer_nb_trailing_newline(nb_str)
            nb = json.loads(nb_str)
        return call(
            func,
            **kwargs,
            nb_path=nb_path,
            out_path=out_path,
            nb=nb,
            indent=indent,
            trailing_newline=trailing_newline,
        )
    return wrapper


def with_nb(func):
    @option('-a', '--ensure-ascii', is_flag=True, help='Octal-escape non-ASCII characters in JSON output')
    @option('-i', '--in-place', is_flag=True, help='Modify [NB_PATH] in-place')
    @option('-n', '--indent', type=int, help='Indentation level for the output notebook JSON (default: infer from input)')
    @option('-o', '--out-path', help='Write to this file instead of stdout')
    @option('-t/-T', '--trailing-newline/--no-trailing-newline', default=None, help='Enforce presence or absence of a trailing newline (default: match input)')
    @with_nb_input
    @wraps(func)
    def wrapper(
        nb_path: str,
        *args,
        out_path: str | None = None,
        ensure_ascii: bool = False,
        in_place: bool = False,
        indent: int | None = None,
        trailing_newline: bool | None = None,
        **kwargs,
    ):
        """Merge consecutive "stream" outputs (e.g. stderr)."""
        if in_place:
            if out_path:
                raise ValueError("Cannot use `-i` with `-o`")
            if not nb_path or nb_path == '-':
                raise ValueError("Cannot use `-i` without explicit `nb_path`")
            out_path = nb_path

        kwargs['nb_path'] = nb_path
        kwargs['out_path'] = out_path
        rv = call(func, *args, **kwargs)
        if isinstance(rv, tuple):
            nb, exc = rv
        elif isinstance(rv, dict):
            nb = rv
            exc = None
        else:
            raise ValueError(f"Unrecognized with_nb return value {type(rv)}: {str(rv)[:100]}")

        if out_path and out_path != '-':
            write_nb(nb, out_path, indent=indent, ensure_ascii=ensure_ascii, trailing_newline=trailing_newline)
        else:
            json.dump(nb, stdout, indent=indent, ensure_ascii=ensure_ascii)
            if trailing_newline:
                print()

        if exc:
            raise exc

    return wrapper


@cli.group()
def nb():
    """Notebook transformation commands (fmt, run, clean, etc.)."""
    pass
