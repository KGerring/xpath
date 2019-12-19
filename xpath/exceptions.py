#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
from __future__ import annotations  # isort:skip
import sys  # isort:skip
import os  # isort:skip
import re  # isort:skip
# stdlib
import contextlib
import importlib



def _try_import(name, *, absolute=False):
    with contextlib.suppress(ModuleNotFoundError, ImportError):
        if absolute:
            return importlib.import_module(name)
        else:
            return importlib.import_module(f".{name}", __package__)
    return None


def __getattr__(name):
    def is_dunder(name):
        """Returns True if a __dunder__ name, False otherwise."""
        return (
            name[:2] == name[-2:] == "__"
            and name[2:3] != "_"
            and name[-3:-2] != "_"
            and len(name) > 4
        )

    if is_dunder(name):
        raise AttributeError(f"dunder {name} not searched")
    result = _try_import(name)
    if result:
        globals()[name] = result
    try:
        return result
    except AttributeError:
        raise AttributeError(f"{name} not found")
    raise AttributeError(f"{name} not found")


class StringException(Exception):
    pass


class XPathSyntaxError(SyntaxError):
    """When we run into an unexpected token, this is the exception to use"""

    def __init__(self, pos=-1, msg="Bad Token"):
        self.pos = pos
        self.msg = msg

    def __repr__(self):
        if self.pos < 0:
            return "#<syntax-error>"
        else:
            return "XPathSyntaxError[@ char " + repr(self.pos) + ": " + self.msg + "]"

    __str__ = __repr__


class NoMoreTokens(Exception):
    """Another exception object, for when we run out of tokens"""

    pass


__all__ = sorted(
    [
        getattr(v, "__name__", k)
        for k, v in list(globals().items())  # export
        if (
            (
                callable(v)
                and getattr(v, "__module__", "")
                == __name__  # callables from this module
                or k.isupper()
            )
            and not getattr(v, "__name__", k).startswith("__")  # or CONSTANTS
        )
    ]
)  # neither marked internal
if __name__ == "__main__":
    print(__file__)
