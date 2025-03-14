from __future__ import annotations

import json
from contextlib import nullcontext
from functools import wraps
from inspect import getfullargspec
from sys import stdin, stdout

from click import argument, group, option
from utz import recvs, call


@group()
def cli():
    pass


def with_nb_input(func):
    spec = getfullargspec(func)

    @wraps(func)
    @argument('nb_path', required=False)
    @argument('out_path', required=False)
    def wrapper(
        nb_path: str | None = None,
        out_path: str | None = None,
        **kwargs,
    ):
        if 'out_path' in kwargs and kwargs['out_path']:
            if out_path != kwargs['out_path']:
                raise ValueError(f"Specify -o/--out-path xor a 2nd positional arg: {out_path} != {kwargs['out_path']}")

        ctx = nullcontext(stdin) if nb_path == '-' or nb_path is None else open(nb_path, 'r')
        with ctx as f:
            nb_str = f.read()
            indent = kwargs.pop('indent', None)
            if indent is None:
                if nb_str.startswith('{'):
                    if nb_str[1] == "\n":
                        idx = 2
                        indent = 0
                        while nb_str[idx] == ' ':
                            idx += 1
                            indent += 1
                    else:
                        indent = None
                else:
                    raise ValueError(f"Cannot infer `indent` from non-JSON input beginning with {nb_str[:30]}")

            trailing_newline = kwargs.pop('trailing_newline', None)
            if trailing_newline is None:
                trailing_newline = nb_str.endswith('\n')
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
        indent: int | None = None,
        trailing_newline: bool | None = None,
        **kwargs,
    ):
        """Merge consecutive "stream" outputs (e.g. stderr)."""
        in_place = kwargs.get('in_place')
        if in_place:
            if out_path:
                raise ValueError("Cannot use `-i` with `-o`")
            if not nb_path or nb_path == '-':
                raise ValueError("Cannot use `-i` without explicit `nb_path`")
            out_path = nb_path
            kwargs['out_path'] = out_path

        kwargs['nb_path'] = nb_path
        rv = call(func, *args, **kwargs)
        if isinstance(rv, tuple):
            nb, exc = rv
        elif isinstance(rv, dict):
            nb = rv
            exc = None
        else:
            raise ValueError(f"Unrecognized with_nb return value {type(rv)}: {str(rv)[:100]}")

        out_ctx = nullcontext(stdout) if out_path == '-' or out_path is None else open(out_path, 'w')
        with out_ctx as f:
            json.dump(nb, f, indent=indent, ensure_ascii=ensure_ascii)
            if trailing_newline:
                f.write('\n')

        if exc:
            raise exc

    return wrapper
