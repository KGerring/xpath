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
try:
    from aenum import Enum
    from typing import NamedTuple
    from collections import namedtuple
except Exception:
    from enum import Enum
    from typing import NamedTuple
    from collections import namedtuple
    

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

class SyntaxException(Exception):
    SYNTAX_ERR_MSG = ("Error parsing expression:\n'%s'\nSyntax error at or near '%s' Line: %d")
    def __init__(self, source, lineNum, location):
        Exception.__init__(self, self.SYNTAX_ERR_MSG % (source, location, lineNum))
        self.source = source
        self.lineNum = lineNum
        self.loc = location


class InternalException(Exception):
    INTERNAL_ERR_MSG = ("Error parsing expression:\n'%s'\nInternal error in processing at or near '%s', Line: %d, Exception: %s")
    def __init__(self, source, lineNum, location, exc, val, tb):
        Exception.__init__(self, self.INTERNAL_ERR_MSG % (source, location, lineNum, exc))
        self.source = source
        self.lineNum = lineNum
        self.loc = location
        self.errorType = exc
        self.errorValue = val
        self.errorTraceback = tb



class ErrorCode(namedtuple('ErrorCode', 'name errorCode message', defaults = ['NONE', 0, 'None'])):
    def get_params(self, args):
        try:
            return self.message % args
        except Exception:
            return self.message

class FtException(Exception):
    def __init__(self, errorCode, args):
        # By defining __str__, args will be available.  Otherwise
        # the __init__ of Exception sets it to the passed in arguments.
        self.errorCode = errorCode
        self.params = args
        self.message = self.errorCode.get_params(args)
        Exception.__init__(self, self.message, args)

    def __str__(self):
        return self.message

CODES =  (ErrorCode('INTERNAL', 1, "There is an internal bug in 4XPath.  Please report this error code to support@4suite.org: %s"),
            ErrorCode('SYNTAX', 2, "There is an internal bug in 4XPath.  Please report this error code to support@4suite.org: %s"),
            ErrorCode('PROCESSING', 3, "There is an internal bug in 4XPath.  Please report this error code to support@4suite.org: %s"),
            ErrorCode('NO_CONTEXT', 10,  "An XPath Context object is required in order to evaluate an expression."),
            ErrorCode('UNDEFINED_VARIABLE', 100, 'Variable undefined: ("%s", "%s").'),
            ErrorCode('UNDEFINED_PREFIX', 101, 'Undefined namespace prefix: "%s".'),
            ErrorCode('WRONG_ARGUMENTS', 200, "Error in arguments to %s: %s"),)
ERRORCODES = {e.name: e for e in CODES}
ERRORNUMS = {e.errorCode: e for e in CODES}

class CompiletimeException(FtException):
    pass
class RuntimeException(FtException):
    pass

COMPILETIME = {num: ERRORNUMS.get(num) for num in (1,2,3) }
RUNTIME = {num: ERRORNUMS.get(num) for num in (1,10,100, 101, 200) }

class MessageSource:
    COMPILETIME = COMPILETIME
    RUNTIME = RUNTIME



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
